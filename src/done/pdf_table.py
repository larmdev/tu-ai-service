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
PAGE_TO_CHECK =47  # 1-based
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def show_newlines(s: str) -> str:
    return (s or "").replace("\n", r"\n")

# --- HELPERS ---
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
    # จัดช่องว่างแบบปลอดภัย
    return " ".join((s or "").replace("\t", " ").split()).strip()

def table_to_markdown(table) -> str:
    """แปลง list-of-rows เป็น markdown table แบบง่าย"""
    if not table:
        return ""
    rows = [[normalize_ws(c) for c in row] for row in table]

    # ใช้แถวแรกเป็น header แบบง่าย ๆ
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    def md_row(r):
        return "| " + " | ".join(r) + " |"

    out = []
    out.append(md_row(header))
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for r in body:
        # เติมช่องให้ครบเท่าหัวตาราง
        if len(r) < len(header):
            r = r + [""] * (len(header) - len(r))
        out.append(md_row(r[: len(header)]))
    return "\n".join(out)

def extract_page_text_and_tables(page) -> str:
    """
    - หา tables พร้อม bbox
    - ดึง text "นอกตาราง" ลดซ้ำ
    - ดึง tables เป็น markdown
    """
    parts = []

    # 1) หา tables (ได้ทั้ง bbox + extract() ของตาราง)
    tables = page.find_tables()  # list of Table objects
    table_bboxes = [t.bbox for t in tables]

    # 2) ดึงข้อความนอกตาราง (ถ้าไม่มีตารางก็เอาทั้งหน้า)
    outside_text_chunks = []

    if not table_bboxes:
        txt = page.extract_text() or ""
        txt = txt.strip()
        if txt:
            outside_text_chunks.append(txt)
    else:
        # สร้าง "โซน" แนวตั้งแบบง่าย: เอา text ในช่วงที่ไม่ทับ bbox ตาราง
        # วิธีนี้เรียบง่ายและได้ผลกับตารางที่วางเป็นบล็อก ๆ
        # - รวม bbox ตารางให้เรียงตาม y0 (บน->ล่าง)
        bxs = sorted(table_bboxes, key=lambda b: b[1])  # (x0,y0,x1,y1)
        top = 0
        for (x0, y0, x1, y1) in bxs:
            # โซนเหนือ table
            if y0 - top > 8:  # กันโซนเล็กเกิน
                crop = page.crop((0, top, page.width, y0))
                txt = (crop.extract_text() or "").strip()
                if txt:
                    outside_text_chunks.append(txt)
            top = max(top, y1)

        # โซนท้ายหน้า
        if page.height - top > 8:
            crop = page.crop((0, top, page.width, page.height))
            txt = (crop.extract_text() or "").strip()
            if txt:
                outside_text_chunks.append(txt)

    outside_text = "\n".join([t for t in outside_text_chunks if t]).strip()
    if outside_text:
        parts.append("[TEXT]")
        parts.append(outside_text)

    # 3) ดึงตาราง
    if tables:
        for idx, t in enumerate(tables, start=1):
            raw = t.extract()  # list-of-rows
            md = table_to_markdown(raw)
            if md.strip():
                parts.append(f"[TABLE {idx}]")
                parts.append(md)

    return "\n\n".join(parts).strip()

# --- MAIN ---
if __name__ == "__main__":
    load_dotenv()

    # 1) Setup Auth (เหมือนเดิม)
    script_dir = Path(__file__).resolve().parent
    potential_paths = [
        script_dir.parent.parent / "service_account.json",
        Path("service_account.json"),
    ]
    sa_path = next((p for p in potential_paths if p.exists()), None)
    if not sa_path:
        raise RuntimeError("Missing service_account.json")

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
