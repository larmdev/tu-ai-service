import io
import re
from pathlib import Path

import pdfplumber
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# --- CONFIG ---
PDF_URL = "https://drive.google.com/file/d/1Z_0zWJQQCrjyEvivrt1lr4ys6FmfkMmO/edit"
PAGE_TO_CHECK = 53  # 1-based
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


# --- HELPERS ---
# ---------------------------
def _extract_file_id_from_drive_url(url: str) -> str:
    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot parse file_id from url: {url}")


def download_drive_pdf_bytes(drive, file_id: str) -> bytes:
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue()


def normalize_ws(s: str) -> str:
    # จัดช่องว่างแบบปลอดภัย (split() จะลบ \n ด้วย)
    return " ".join((s or "").replace("\t", " ").split()).strip()


# ---------------------------
# Table -> Markdown
# ---------------------------
def table_to_markdown(table) -> str:
    """แปลง list-of-rows เป็น markdown table แบบง่าย"""
    if not table:
        return ""

    rows = [[normalize_ws(c) for c in row] for row in table]

    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    def md_row(r):
        return "| " + " | ".join(r) + " |"

    out = []
    out.append(md_row(header))
    out.append("| " + " | ".join(["---"] * len(header)) + " |")

    for r in body:
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        out.append(md_row(r[: len(header)]))

    return "\n".join(out)


# ---------------------------
# Geometry helpers (bbox)
# ---------------------------
def _word_center(word):
    return ((word["x0"] + word["x1"]) / 2.0, (word["top"] + word["bottom"]) / 2.0)


def _in_bbox(x, y, bbox, pad=1.0):
    # bbox = (x0, y0, x1, y1)
    x0, y0, x1, y1 = bbox
    return (x0 - pad) <= x <= (x1 + pad) and (y0 - pad) <= y <= (y1 + pad)


# ---------------------------
# Words -> Lines -> Paragraphs
# ---------------------------
def _build_line(line_words, char_tol=1.5):
    line_words = sorted(line_words, key=lambda w: w["x0"])
    parts = []
    last_x1 = None

    x0 = min(w["x0"] for w in line_words)
    x1 = max(w["x1"] for w in line_words)
    top = min(w["top"] for w in line_words)
    bottom = max(w["bottom"] for w in line_words)

    for w in line_words:
        # เว้นวรรคตามระยะห่างจริง
        if last_x1 is not None and (w["x0"] - last_x1) > char_tol:
            parts.append(" ")
        parts.append(w["text"])
        last_x1 = w["x1"]

    text = "".join(parts).strip()
    return {"top": top, "bottom": bottom, "x0": x0, "x1": x1, "text": text}


def _group_words_to_lines(words, line_tol=3.0, char_tol=1.5):
    """
    แปลง words -> lines (แต่ละ line มี top/bottom/x0 + text)
    """
    if not words:
        return []

    words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    lines = []
    cur_words = []
    cur_top = words[0]["top"]

    for w in words:
        if abs(w["top"] - cur_top) > line_tol:
            if cur_words:
                lines.append(_build_line(cur_words, char_tol=char_tol))
            cur_words = [w]
            cur_top = w["top"]
        else:
            cur_words.append(w)

    if cur_words:
        lines.append(_build_line(cur_words, char_tol=char_tol))

    return lines


def _lines_to_paragraph_text(lines, para_gap=6.0, indent_gap=14.0):
    """
    รวม lines -> ข้อความที่มี "ย่อหน้า"
    - เว้นบรรทัดเมื่อ gap ระหว่างบรรทัดมาก (para_gap)
    - หรือมีการย่อหน้า (indent) เปลี่ยนชัดเจน (indent_gap)
    """
    if not lines:
        return ""

    out_lines = []
    prev = None

    for ln in lines:
        if not ln.get("text"):
            continue

        if prev is None:
            out_lines.append(ln["text"])
            prev = ln
            continue

        vertical_gap = ln["top"] - prev["bottom"]
        indent_delta = ln["x0"] - prev["x0"]

        new_para = (vertical_gap > para_gap) or (indent_delta > indent_gap)

        if new_para:
            out_lines.append("")  # blank line = new paragraph
            out_lines.append(ln["text"])
        else:
            out_lines.append(ln["text"])

        prev = ln

    return "\n".join(out_lines).strip()


# ---------------------------
# Main extraction: keep real order (text + tables)
# ---------------------------
def extract_page_text_and_tables(page) -> str:
    """
    ทำให้ output “ตามตำแหน่งจริง”
    - สร้าง block ของ (1) บรรทัดข้อความนอกตาราง และ (2) ตาราง
    - sort บน->ล่าง, ซ้าย->ขวา
    - พิมพ์สลับกัน พร้อมย่อหน้า
    """
    parts = []

    # 1) หา tables + bbox
    tables = page.find_tables()
    table_bboxes = [t.bbox for t in tables]  # (x0,y0,x1,y1)

    # 2) ดึงคำทั้งหมดในหน้า
    words = page.extract_words(
        keep_blank_chars=False,
        use_text_flow=True,
        extra_attrs=["fontname", "size"],
    ) or []

    # 3) กรองคำที่อยู่ในตารางออก
    outside_words = []
    for w in words:
        cx, cy = _word_center(w)
        inside_any = any(_in_bbox(cx, cy, bbox, pad=1.0) for bbox in table_bboxes)
        if not inside_any:
            outside_words.append(w)

    # 4) outside_words -> lines
    text_lines = _group_words_to_lines(outside_words, line_tol=3.0, char_tol=1.5)

    # 5) สร้าง blocks ของ line + table ตามตำแหน่งจริง
    blocks = []

    for ln in text_lines:
        blocks.append({
            "kind": "line",
            "top": ln["top"],
            "x0": ln["x0"],
            "payload": ln,
        })

    for idx, t in enumerate(tables, start=1):
        x0, y0, x1, y1 = t.bbox
        blocks.append({
            "kind": "table",
            "top": y0,
            "x0": x0,
            "payload": {"index": idx, "table": t},
        })

    blocks.sort(key=lambda b: (b["top"], b["x0"]))

    # 6) เดิน blocks: สะสม line เป็นย่อหน้า แล้วแทรกตารางตรงจุดจริง
    pending_lines = []

    def flush_text():
        nonlocal pending_lines
        if pending_lines:
            text = _lines_to_paragraph_text(pending_lines, para_gap=6.0, indent_gap=14.0)
            if text.strip():
                parts.append("[TEXT]")
                parts.append(text)
            pending_lines = []

    for b in blocks:
        if b["kind"] == "line":
            pending_lines.append(b["payload"])
        else:
            flush_text()
            idx = b["payload"]["index"]
            t = b["payload"]["table"]
            raw = t.extract()
            md = table_to_markdown(raw)
            if md.strip():
                parts.append(f"[TABLE {idx}]")
                parts.append(md)

    flush_text()

    return "\n\n".join([p for p in parts if p and p.strip()]).strip()


# --- MAIN ---
if __name__ == "__main__":
    load_dotenv()

    # 1) Setup Auth
    script_dir = Path(__file__).resolve().parent
    potential_paths = [
        script_dir.parent.parent / "service_account.json",
        Path("service_account.json"),
    ]
    sa_path = next((p for p in potential_paths if p.exists()), None)
    if not sa_path:
        raise RuntimeError("Missing service_account.json (place it next to script or at ../../service_account.json)")

    creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    # 2) Download PDF
    file_id = _extract_file_id_from_drive_url(PDF_URL)
    print(f"[INFO] Downloading PDF (ID: {file_id})...")
    pdf_bytes = download_drive_pdf_bytes(drive, file_id)
    print(f"[INFO] Downloaded {len(pdf_bytes)} bytes.")

    # 3) Analyze page
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        page_index = PAGE_TO_CHECK - 1
        if page_index < 0 or page_index >= len(pdf.pages):
            print(f"[ERROR] Page {PAGE_TO_CHECK} not found. Max pages: {len(pdf.pages)}")
        else:
            page = pdf.pages[page_index]
            print("-" * 60)
            print(f"PAGE {PAGE_TO_CHECK} (index {page_index})")
            print("-" * 60)

            output = extract_page_text_and_tables(page)
            print(output if output else "[EMPTY] No text/tables extracted.")
