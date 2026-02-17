# main_local_save_parallel.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json
import asyncio
import re
import requests
import urllib.parse
import logging
import sys
from typing import Optional, Any, Dict, List, Tuple

# --- your functions ---
from function.fn_gemini import call_openrouter_pdf   # <- sync function (requests)
from function.fn_slice_page_pdf import slice_pdf_pages
from function.fn_chunk_number import locate_chunks
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


        # --- select schema/prompt ---
        if chunk_idx == 0:
            from fn_chunk.fn_chunk1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 1:
            from fn_chunk.fn_chunk2 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 2:
            from fn_chunk.fn_chunk3 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 3:
            from fn_chunk.fn_chunk4_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 5:
            from fn_chunk.fn_chunk5_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 6:
            from fn_chunk.fn_chunk6_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 7:
            from fn_chunk.fn_chunk7 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 8:
            from fn_chunk.fn_chunk8 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        elif chunk_idx == 9:
            from fn_chunk.fn_chunk9 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
        else:
            logger.warning(f"[{fileName}] Unknown chunk_idx={chunk_idx}, skip.")
            return

        # -----------------------------
        # ✅ data1 (async wrapper)
        # -----------------------------
        data1 = await asyncio.to_thread( call_openrouter_pdf_async,
            semaphore,
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=chunk_pdf_bytes,
            text=text,
            engine="pdf-text",
            temperature=0.0,
        )

        # -----------------------------
        # clean ตาม chunk
        # -----------------------------
        if chunk_idx == 0:
            from regex.fn_clean1 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        elif chunk_idx == 1:
            from regex.fn_clean2 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        elif chunk_idx == 2:
            from regex.fn_clean3 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        elif chunk_idx == 3:
            # data2
            from fn_chunk.fn_chunk4_1_2 import schema_prompt as sp2
            schema2, prompt2 = sp2(chunk_pdf_bytes=chunk_pdf_bytes)
            data2 = await asyncio.to_thread(call_openrouter_pdf_async,
                semaphore,
                api_key=OPEN_ROUTER_KEY,
                model=MODEL,
                prompt=prompt2,
                schema=schema2,
                pdf_bytes=chunk_pdf_bytes,
                text=None,
                engine="pdf-text",
                temperature=0.0,
            )

            # data3 ใช้ chunk ถัดไป
            from fn_chunk.fn_chunk4_2 import schema_prompt as sp3
            schema3, prompt3 = sp3(chunk_pdf_bytes=chunk_pdf_bytes)

            start_page2 = start_chunk_page[chunk_idx + 1]
            end_page2 = start_chunk_page[chunk_idx + 2]
            data3 = None

            if start_page2 is not None and end_page2 is not None:
                chunk_pdf_bytes2 = slice_pdf_pages(
                    pdf_bytes=pdf_bytes,
                    start_page=start_page2,
                    end_page=end_page2,
                )
                data3 = await asyncio.to_thread (call_openrouter_pdf_async,
                    semaphore,
                    api_key=OPEN_ROUTER_KEY,
                    model=MODEL,
                    prompt=prompt3,
                    schema=schema3,
                    pdf_bytes=chunk_pdf_bytes2,
                    text=None,
                    engine="pdf-text",
                    temperature=0.0,
                )

            from regex.fn_clean4 import clean
            data1 = clean(master_schema=master_schema, data1=data1, data2=data2, data3=data3)

        elif chunk_idx == 5:
            # data2 (text with tables)
            from fn_chunk.fn_chunk5_1_2 import schema_prompt as sp2
            schema2, prompt2 = sp2(chunk_pdf_bytes=chunk_pdf_bytes)

            text_tbl = text_with_tables(chunk_pdf_bytes)
            data2 = await asyncio.to_thread(call_openrouter_pdf_async,
                semaphore,
                api_key=OPEN_ROUTER_KEY,
                model=MODEL,
                prompt=prompt2,
                schema=schema2,
                pdf_bytes=None,
                text=text_tbl,
                engine="pdf-text",
                temperature=0.0,
            )

            # data3
            from fn_chunk.fn_chunk5_1_3 import schema_prompt as sp3
            schema3, prompt3 = sp3(chunk_pdf_bytes=chunk_pdf_bytes)
            data3 = await asyncio.to_thread(call_openrouter_pdf_async,
                semaphore,
                api_key=OPEN_ROUTER_KEY,
                model=MODEL,
                prompt=prompt3,
                schema=schema3,
                pdf_bytes=chunk_pdf_bytes,
                text=None,
                engine="pdf-text",
                temperature=0.0,
            )

            from regex.fn_clean5 import clean
            data1 = clean(master_schema=master_schema, data1=data1, data2=data2, data3=data3)

        elif chunk_idx == 6:
            from fn_chunk.fn_chunk6_1_2 import schema_prompt as sp2
            schema2, prompt2 = sp2(chunk_pdf_bytes=chunk_pdf_bytes)

            data2 = await asyncio.to_thread(call_openrouter_pdf_async,
                semaphore,
                api_key=OPEN_ROUTER_KEY,
                model=MODEL,
                prompt=prompt2,
                schema=schema2,
                pdf_bytes=chunk_pdf_bytes,
                text=None,
                engine="pdf-text",
                temperature=0.0,
            )

            from regex.fn_clean6 import clean
            data1 = clean(master_schema=master_schema, data1=data1, data2=data2)

        elif chunk_idx == 7:
            from regex.fn_clean7 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        elif chunk_idx == 8:
            from regex.fn_clean8 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        elif chunk_idx == 9:
            from regex.fn_clean9 import clean
            data1 = clean(master_schema=master_schema, data1=data1)

        # -----------------------------
        # reorder (optional)
        # -----------------------------
        if data1:
            data1 = reorder_by_schema(data1, master_schema)

        # -----------------------------
        # Save JSON
        # -----------------------------
        save_dir = os.path.join(TARGET_BASE_DIR, fileName)
        os.makedirs(save_dir, exist_ok=True)

        # section naming (match your old: g{section}.json)
        # old logic: if chunk_idx < 4 -> +1 else same
        # chunk 0..3 => g1..g4 , chunk 5..9 => g5..g9
        if chunk_idx < 4:
            section_str = str(chunk_idx + 1)
        else:
            section_str = str(chunk_idx)

        file_path = os.path.join(save_dir, f"g{section_str}.json")

        output_content = {
            "fileName": fileName,
            "section": section_str,
            "data": data1,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_content, f, ensure_ascii=False, indent=4)

        logger.info(f"[{fileName}] ✅ Saved Section {section_str} -> {file_path}")

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP Error: {http_err}"
        if http_err.response is not None:
            error_msg += f" | API Response: {http_err.response.text}"
        logger.error(f"[{fileName}] ❌ Error Section {section_str}: {error_msg}", exc_info=True)

    except Exception as e:
        logger.error(f"[{fileName}] ❌ Error Section {section_str}: {e}", exc_info=True)


# -------------------------
# Background Manager (parallel)
# -------------------------
async def background_manager(refId: str, url: str):
    try:
        logger.info(f"🚀 [Job Started] RefID: {refId} | URL: {url}")

        pdf_bytes, folder_name = load_pdf_and_name(url)

        chunks_map = locate_chunks(pdf_bytes=pdf_bytes, debug=False)
        start_chunk_page = [v for k, v in chunks_map.items() if k != "last_page"]

        logger.info(f"[{folder_name}] Structure detected. Found {len(start_chunk_page)-1} chunks to process.")

        # ✅ จำกัด concurrency ทั้งงานด้วย semaphore (เช่น 3 งานพร้อมกัน)
        semaphore = asyncio.Semaphore(3)

        tasks = []
        for i in range(len(start_chunk_page) - 1):
            if start_chunk_page[i] is None or start_chunk_page[i + 1] is None:
                continue

            tasks.append(
                process_and_save_chunk(
                    chunk_idx=i,
                    pdf_bytes=pdf_bytes,
                    fileName=folder_name,
                    start_chunk_page=start_chunk_page,
                    semaphore=semaphore,
                )
            )

        if tasks:
            # ✅ นี่คือจุดที่ทำให้มัน "parallel/concurrent" จริง
            await asyncio.gather(*tasks)
            logger.info(f"[{folder_name}] 🎉 All tasks finished successfully!")
        else:
            logger.warning(f"[{folder_name}] No tasks created.")

    except Exception as e:
        logger.error(f"Background Task Global Failed for {url}: {e}", exc_info=True)


# -------------------------
# API Endpoint
# -------------------------
@app.post("/api/curriculum/local-save")
async def extract_curr_local(body: ChunkRequest, background_tasks: BackgroundTasks):
    if not body.url:
        raise HTTPException(status_code=400, detail="url is required")

    background_tasks.add_task(background_manager, body.refId, body.url)
    logger.info(f"Accepted request for {body.url} (Ref: {body.refId})")

    return {
        "status": 200,
        "message": "Processing started. Check logs/app.log for progress.",
    }
