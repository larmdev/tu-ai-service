
from function.fn_gemini import call_openrouter_pdf
from function.fn_slice_page_pdf import slice_pdf_pages
from function.fn_pdf_to_byte import to_pdf_bytes
from function.fn_chunk_number import locate_chunks
from function.fn_pdf_text_table import text_with_tables
from function.fn_reorder_data_by_schema import reorder_by_schema
from function.fn_concat_pdf_bytes import concat_pdf_bytes
from function.fn_find_fisrt_page_non_empty import find_first_page_non_empty
import os
import json


import sys
import sys
class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()

def setup_logging_to_file(log_path: str = "1log_test.log", mode: str = "w", encoding: str = "utf-8"):
    """
    ทำให้ print() ยังออก terminal และถูกเขียนลงไฟล์ log พร้อมกัน
    คืนค่าเป็นฟังก์ชัน close() เอาไว้เรียกตอนจบ
    """
    log_file = open(log_path, mode, encoding=encoding)

    # เก็บของเดิมไว้ เผื่อ restore
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys.stdout = _Tee(sys.__stdout__, log_file)
    sys.stderr = _Tee(sys.__stderr__, log_file)

    def close():
        # restore กลับเหมือนเดิม + ปิดไฟล์
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        log_file.close()

    return close



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
list_pdf = [
    "https://drive.google.com/file/d/1Z1yqquXlgKTRaK7AEBGMV2fbxUqti3kO/edit",
    # "https://drive.google.com/file/d/1EnjPZeeDrSA8ihlqJfHVhAg84uwkXQ2k/edit",
    # "https://drive.google.com/file/d/1I9qBUchBydejWwGgbkpC-IdZFvfg61G-/edit",
    # "https://drive.google.com/file/d/1BuRHEYFGX0uQRJaiAG_Wo8TLnuZfxIZa/edit",
    # "https://drive.google.com/file/d/1Z_0zWJQQCrjyEvivrt1lr4ys6FmfkMmO/edit",
    # "https://drive.google.com/file/d/1gZf4ob2MscXVIodVEDe_Y5RhWfy02On9/view"   
]
close_log = setup_logging_to_file("1log_test.log", mode="w")  # "a" ต่อท้าย, "w" ทับไฟล์เดิม

try:

    load_dotenv()
    OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
    print(OPEN_ROUTER_KEY)
    MODEL = os.getenv("MODEL")

    drive_url = os.getenv("DRIVE_URL")
    script_dir = Path(__file__).resolve().parent

    # 2. ถอยหลัง 1 ชั้นเพื่อไปหาโฟลเดอร์หลัก (จะได้ .../curriculum_tu)
    # หมายเหตุ: .parent 1 ครั้ง เพราะไฟล์อยู่ใน src (1 ชั้นจาก root)
    project_root = script_dir.parent 

    # 3. รวม path เข้ากับชื่อไฟล์
    sa_path = project_root / "service_account.json"
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

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
    #####



    for i in list_pdf:
        PDF_URL = i
        print(f"PDF: {i}")
        file_id = _extract_file_id_from_drive_url(PDF_URL)
        pdf_bytes = download_drive_pdf_bytes(drive, file_id)
        print('already download file')

        start_chunk_page = [v for k, v in locate_chunks(pdf_bytes= pdf_bytes, debug= False).items() if k not in ( "last_page")]
        
        # start_chunk_page = [x if i == 5 or i == 6 else None for i, x in enumerate(start_chunk_page)]


        for i, x in enumerate(start_chunk_page):
            if x is None:
                continue
            
        print(start_chunk_page)
        for i in range(len(start_chunk_page)-1) :
            if i != 1:
                continue ####################################
            if i == 4 :
                continue
            start_page = start_chunk_page[i]
            end_page = start_chunk_page[i + 1]
            print("                -------------             ")
            
            print("i =",i,"->",start_page,"and",end_page)

            if start_page is None or end_page is None :
                continue
            chunk_pdf_bytes = slice_pdf_pages(
                pdf_bytes=pdf_bytes,
                start_page=start_page,
                end_page=end_page
            )

            text = None

            if i == 0:
                number_first_have_text = find_first_page_non_empty(pdf_bytes=pdf_bytes)
                chunk_pdf_bytes2 = slice_pdf_pages(pdf_bytes=pdf_bytes,start_page=number_first_have_text,end_page=number_first_have_text)
                chunk_pdf_bytes = concat_pdf_bytes(chunk_pdf_bytes2,chunk_pdf_bytes)


            if i == 0 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk1 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 1 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk2 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 2 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk3 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 3 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk4_1_1 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 4 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk4_2 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 5 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk5_1_1 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

                # text = text_with_tables(chunk_pdf_bytes)
                # chunk_pdf_bytes = None

            elif i == 6 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk6_1_1 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 7 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk7 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 8 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk8 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            elif i == 9 and start_page is not None and end_page is not None:
                from fn_chunk.fn_chunk9 import schema_prompt
                schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            data1 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )

            if i == 0:
                from regex.fn_clean1 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            if i == 1:
                from regex.fn_clean2 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            if i == 2:
                from regex.fn_clean3 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            if i == 3 :
                from fn_chunk.fn_chunk4_1_2 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
                data2 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                    engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                    temperature=0.00,
                )

                from fn_chunk.fn_chunk4_2 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

                start_page = start_chunk_page[i+1]
                end_page = start_chunk_page[i+2]
                chunk_pdf_bytes = slice_pdf_pages(
                    pdf_bytes=pdf_bytes,
                    start_page=start_page,
                    end_page=end_page
                )

                data3 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                    engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                    temperature=0.00,
                )

                from regex.fn_clean4 import clean
                data1 = clean (master_schema=master_schema,data1=data1,data2=data2,data3=data3)

            if i == 5 :
                from fn_chunk.fn_chunk5_1_2 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
                text = text_with_tables(chunk_pdf_bytes)
                chunk_pdf_bytes2 = None
                data2 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes2,text = text,
                    engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                    temperature=0.00,
                )
                text=None

                from fn_chunk.fn_chunk5_1_3 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
                data3 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                    engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                    temperature=0.00,
                )

                from regex.fn_clean5 import clean
                data1 = clean (master_schema=master_schema,data1=data1,data2=data2,data3=data3)

            if i == 6 :
                from fn_chunk.fn_chunk6_1_2 import schema_prompt
                schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
                data2 = call_openrouter_pdf(api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                    engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                    temperature=0.00,
                )

                from regex.fn_clean6 import clean
                data1 = clean (master_schema=master_schema,data1=data1,data2=data2)

            if i == 7:
                from regex.fn_clean7 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            if i == 8:
                from regex.fn_clean8 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            if i == 9:
                from regex.fn_clean9 import clean
                data1 = clean (master_schema=master_schema,data1=data1)

            print("<data before reoreder>",data1)
            print("<master_schema>",master_schema)
            data1 = reorder_by_schema(data1, master_schema)
            print("<data after reorder>")
            print(json.dumps(data1, ensure_ascii=False, indent=2))
            print("done")


finally:
    close_log()