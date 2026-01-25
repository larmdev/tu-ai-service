import io
import re
import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ✅ ใส่ URL ของไฟล์ PDF ตรงนี้ (ไม่ใช่โฟลเดอร์)
PDF_URL = "https://drive.google.com/file/d/1I9qBUchBydejWwGgbkpC-IdZFvfg61G-/edit"
page_to_check = 78
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _extract_file_id_from_drive_url(url: str) -> str:
    # รองรับ /file/d/<id> และ ?id=<id>
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


def _escape_non_printable_keep_thai(s: str) -> str:
    out = []
    for ch in s:
        code = ord(ch)

        # keep common whitespace
        if ch in ("\n", "\r", "\t"):
            out.append(ch)
            continue

        # escape other control characters
        if code < 0x20 or (0x7F <= code <= 0x9F):
            out.append(f"\\u{code:04x}")
            continue

        # keep printable chars (Thai/English/etc.)
        if ch.isprintable():
            out.append(ch)
            continue

        # escape anything else
        if code <= 0xFFFF:
            out.append(f"\\u{code:04x}")
        else:
            out.append(f"\\U{code:08x}")

    return "".join(out)


def extract_page_text_as_debug_string(pdf_bytes: bytes, page_num_1indexed: int) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("PDF has 0 pages or cannot be read.")

    if page_num_1indexed < 1 or page_num_1indexed > total_pages:
        raise ValueError(f"page_num out of range: {page_num_1indexed} (PDF has {total_pages} pages)")

    raw = reader.pages[page_num_1indexed - 1].extract_text() or ""
    return _escape_non_printable_keep_thai(raw)


if __name__ == "__main__":
    load_dotenv()

    # (optional) คุณจะเก็บ DRIVE_URL ไว้ก็ได้ แต่ไฟล์นี้ใช้ PDF_URL เป็นหลัก
    drive_url = os.getenv("DRIVE_URL", "")
    if drive_url:
        print("[INFO] DRIVE_URL from .env =", drive_url)

    script_dir = Path(__file__).resolve().parent
        
    # ถอยหลัง 2 ชั้น (จาก done -> src -> curriculum_tu) เพื่อหา service_account.json
    # หรือถ้าหาไม่เจอ ให้ลองหาในโฟลเดอร์ปัจจุบันดู
    potential_paths = [
        script_dir.parent.parent / "service_account.json", # หาที่ root
        Path("service_account.json")                       # หาที่ปัจจุบัน
    ]
    
    sa_path = None
    for p in potential_paths:
        if p.exists():
            sa_path = p
            break
        
    if not sa_path.exists():
        raise RuntimeError(f"Missing service_account.json in current dir: {Path.cwd()}")



    creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    file_id = _extract_file_id_from_drive_url(PDF_URL)
    pdf_bytes = download_drive_pdf_bytes(drive, file_id)

    print("[OK] file_id =", file_id)
    print("[OK] downloaded bytes =", len(pdf_bytes))
    print("[HEAD]", pdf_bytes[:20])

    if not pdf_bytes.startswith(b"%PDF"):
        print("[WARN] bytes ไม่ขึ้นต้นด้วย %PDF อาจเป็น error/permission page")

    text = extract_page_text_as_debug_string(pdf_bytes, page_to_check)
    print("\n[PAGE TEXT]")
    print(text)
