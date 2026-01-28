from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_pdf_to_byte import to_pdf_bytes
from fn_chunk_number import locate_chunks
import os
import json

#####
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
from typing import Any, Dict
from pathlib import Path
from done.read_text import extract_page_text_as_debug_string

# --- ส่วนที่แก้ไข: เปลี่ยนชื่อไฟล์เป็น .log ---
LOG_FILE = "1log_test.log"

# (Optional) ล้างไฟล์เก่าก่อนเริ่มรันใหม่
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"=== Start Log ===\n")

def log_print(*args):
    """ฟังก์ชันปริ้นออกหน้าจอและเขียนลงไฟล์ log"""
    # แปลงทุก argument เป็น string แล้วรวมกัน
    message = " ".join(map(str, args))
    
    # 1. ปริ้นออกจอ
    print(message)
    
    # 2. เขียนลงไฟล์ .log (Mode 'a' คือ append ต่อท้าย)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
# ----------------------------------------

list_pdf = [
    "https://drive.google.com/file/d/1Z1yqquXlgKTRaK7AEBGMV2fbxUqti3kO/edit",
    "https://drive.google.com/file/d/1EnjPZeeDrSA8ihlqJfHVhAg84uwkXQ2k/edit",
    "https://drive.google.com/file/d/1I9qBUchBydejWwGgbkpC-IdZFvfg61G-/edit",
    "https://drive.google.com/file/d/1BuRHEYFGX0uQRJaiAG_Wo8TLnuZfxIZa/edit",
    "https://drive.google.com/file/d/1Z_0zWJQQCrjyEvivrt1lr4ys6FmfkMmO/edit",
    "https://drive.google.com/file/d/1gZf4ob2MscXVIodVEDe_Y5RhWfy02On9/view"                                                                             
]

load_dotenv()
OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")

drive_url = os.getenv("DRIVE_URL")
script_dir = Path(__file__).resolve().parent

project_root = script_dir.parent 

sa_path = project_root / "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
drive = build("drive", "v3", credentials=creds, cache_discovery=False)

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
#####


def reorder_by_schema(data: Any, schema: Dict[str, Any]) -> Any:
    if data is None:
        return None

    schema_type = schema.get("type")
    is_object = schema_type == "object" or (isinstance(schema_type, list) and "object" in schema_type)
    is_array  = schema_type == "array"  or (isinstance(schema_type, list) and "array" in schema_type)

    if is_object and isinstance(data, dict):
        props = schema.get("properties", {})
        ordered: Dict[str, Any] = {}

        for k, k_schema in props.items(): 
            v = data.get(k, None)
            ordered[k] = reorder_by_schema(v, k_schema)

        return ordered

    if is_array and isinstance(data, list):
        items_schema = schema.get("items", {})
        items_type = items_schema.get("type")
        items_is_object = items_type == "object" or (isinstance(items_type, list) and "object" in items_type)

        if items_is_object:
            return [reorder_by_schema(item, items_schema) for item in data]

        return data

    return data

for i_pdf, pdf_url in enumerate(list_pdf):
    PDF_URL = pdf_url
    
    # ใช้ log_print แทน print
    log_print(f"PDF URL: {pdf_url}")
    
    file_id = _extract_file_id_from_drive_url(PDF_URL)
    pdf_bytes = download_drive_pdf_bytes(drive, file_id)
    
    log_print('already download file')

    start_chunk_page = [v for k, v in locate_chunks(pdf_bytes= pdf_bytes, debug= False).items() if k not in ( "last_page")]
    
    start_chunk_page = [x if i == 6 or i == 5 else None for i, x in enumerate(start_chunk_page)]

    for i, x in enumerate(start_chunk_page):
        if x is None:
            continue
        
    log_print(f"Chunk Pages: {start_chunk_page}")

    for i in range(len(start_chunk_page)-1) :
        start_page = start_chunk_page[i]
        end_page = start_chunk_page[i + 1]

        log_print("                 -------------             ")
        log_print("i =", i, "->", start_page, "and", end_page)

        if start_page is None or end_page is None :
            continue

        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        if i == 0 and start_page is not None and end_page is not None:
            log_print("do 1")
            from fn_chunk1 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 1 and start_page is not None and end_page is not None:
            from fn_chunk2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 2 and start_page is not None and end_page is not None:
            from fn_chunk3 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 3 and start_page is not None and end_page is not None:
            from fn_chunk4_1 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 4 and start_page is not None and end_page is not None:
            from fn_chunk4_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 5 and start_page is not None and end_page is not None:
            from fn_chunk5 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 6 and start_page is not None and end_page is not None:
            from fn_chunk6 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 7 and start_page is not None and end_page is not None:
            from fn_chunk7 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 8 and start_page is not None and end_page is not None:
            from fn_chunk8 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 9 and start_page is not None and end_page is not None:
            from fn_chunk9 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        
        else:
            continue

        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=chunk_pdf_bytes,
            engine="pdf-text", 
            temperature=0.02,
        )

        data = reorder_by_schema(data, schema)
        
        # Log JSON ลงไฟล์
        log_print(json.dumps(data, ensure_ascii=False, indent=2))