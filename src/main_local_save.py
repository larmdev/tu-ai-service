from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
import json
import asyncio
import re
import requests
import urllib.parse
from dotenv import load_dotenv
import logging
import sys

# Import ฟังก์ชันของคุณ
# ตรวจสอบว่าไฟล์เหล่านี้อยู่ในโฟลเดอร์เดียวกับ main หรือใน src ตามที่ตั้งค่า Docker
from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_chunk_number import locate_chunks
from fn_reorder_data_by_schema import reorder_data_by_schema

load_dotenv()

# --- 1. ตั้งค่า Logger ---
# สร้างโฟลเดอร์ logs ถ้ายังไม่มี
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ตั้งค่า Logging Config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"), # บันทึกลงไฟล์
        logging.StreamHandler(sys.stdout) # แสดงผลที่หน้าจอด้วย
    ]
)
logger = logging.getLogger(__name__)

OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")
# ใช้ Path จาก ENV ถ้ามี (สำหรับ Docker) ถ้าไม่มีให้ใช้ Path ในเครื่อง
DEFAULT_LOCAL_PATH = os.path.expanduser("~/Desktop/pimdej/curriculum_tu/data")
TARGET_BASE_DIR = os.getenv("OUTPUT_DIR", DEFAULT_LOCAL_PATH)

app = FastAPI()

class ChunkRequest(BaseModel):
    refId: str
    url: str

# ฟังก์ชันช่วยแก้ภาษาต่างดาว (Mojibake)
def fix_utf8(text):
    if not text: return text
    try:
        # ลองแปลงจาก Latin-1 กลับเป็น UTF-8 (แก้ปัญหา à¸¨à¸...)
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

def get_google_drive_direct_link(url: str):
    patterns = [
        r"drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)"
    ]
    file_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            break
    
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={file_id}", file_id
    return url, None

def load_pdf_and_name(url: str):
    logger.info(f"Start downloading: {url}")
    direct_url, file_id = get_google_drive_direct_link(url)
    
    try:
        response = requests.get(direct_url)
        response.raise_for_status()
        
        filename = None
        # พยายามหาชื่อไฟล์จาก Header
        if "content-disposition" in response.headers:
            cd = response.headers["content-disposition"]
            fname_match = re.search(r'filename="?([^"]+)"?', cd)
            if fname_match:
                filename = fname_match.group(1)
            elif "filename*" in cd:
                 fname_match = re.search(r"filename\*=UTF-8''(.+)", cd)
                 if fname_match:
                     filename = urllib.parse.unquote(fname_match.group(1))

        # Fallback ถ้าหาชื่อไม่เจอ
        if not filename:
            if file_id:
                filename = f"gdrive_{file_id}"
            else:
                filename = url.split("/")[-1].split("?")[0] or "unknown_file"

        # --- แก้ไขจุดนี้: แปลง encoding ให้ถูกต้อง ---
        filename = fix_utf8(filename) 
        # ----------------------------------------

        # ลบนามสกุลไฟล์เพื่อทำเป็นชื่อ Folder
        if filename.lower().endswith(".pdf"):
            folder_name = filename[:-4]
        else:
            folder_name = filename

        # ล้างชื่อไฟล์ (อนุญาตภาษาไทย แต่ลบอักขระพิเศษของระบบไฟล์)
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
        
        logger.info(f"Download complete. Resolved Name: {folder_name}")
        return response.content, folder_name

    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        raise Exception(f"Download failed: {e}")

async def process_and_save_chunk(chunk_idx, start_page, end_page, pdf_bytes, fileName, start_chunk_page):
    section_str = "Unknown"
    try:
        # --- Config Mapping ---
        chunk_config = {
            0: {"module": "fn_chunk1",   "section": "1"},
            1: {"module": "fn_chunk2",   "section": "2"},
            2: {"module": "fn_chunk3",   "section": "3"},
            3: {"module": "fn_chunk4_1", "section": "4_1"},
            4: {"module": "fn_chunk4_2", "section": "4_2"},
            5: {"module": "fn_chunk5",   "section": "5"},
            6: {"module": "fn_chunk6",   "section": "6"},
            7: {"module": "fn_chunk7",   "section": "7"},
            8: {"module": "fn_chunk8",   "section": "8"},
            9: {"module": "fn_chunk9",   "section": "9"},
        }

        if chunk_idx not in chunk_config:
            return

        config = chunk_config[chunk_idx]
        module_name = config["module"]
        section_str = config["section"]

        logger.info(f"[{fileName}] Processing Section {section_str} (Pages {start_page}-{end_page})...")

        # Dynamic Import
        module = __import__(module_name, fromlist=['schema_prompt'])
        schema, prompt = module.schema_prompt()

        if prompt is None: 
            logger.warning(f"[{fileName}] Section {section_str}: Prompt is None, skipping.")
            return

        # Slice PDF
        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes, start_page=start_page, end_page=end_page
        )

        # AI Process
        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY, model=MODEL, prompt=prompt, schema=schema,
            pdf_bytes=chunk_pdf_bytes, engine="pdf-text", temperature=0.00,
        )
        
        if data:
        # เรียกใช้ฟังก์ชันจัดเรียง (data จะถูกเรียง key ใหม่ตาม schema เป๊ะๆ)
            logger.info(data)
            data = reorder_data_by_schema(data, schema)
            logger.info(f"-------- reorder --------\n{data}")

        # Save File
        save_dir = os.path.join(TARGET_BASE_DIR, fileName)
        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, f"g{section_str}.json")

        output_content = {
            "fileName": fileName,
            "section": section_str,
            "data": data
        }

        

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output_content, f, ensure_ascii=False, indent=4)
        
        logger.info(f"[{fileName}] ✅ Saved Section {section_str} -> {file_path}")

    except requests.exceptions.HTTPError as http_err:
        # ดักจับ Error จาก API โดยเฉพาะ เพื่อดูว่า OpenRouter ตอบอะไรกลับมา
        error_msg = f"HTTP Error: {http_err}"
        if http_err.response is not None:
            # นี่คือจุดสำคัญที่จะบอกว่าทำไมถึง 400 Bad Request
            error_detail = http_err.response.text
            error_msg += f" | API Response: {error_detail}"
        
        logger.error(f"[{fileName}] ❌ Error Section {section_str}: {error_msg}")

    except Exception as e:
        logger.error(f"[{fileName}] ❌ Error Section {section_str}: {e}", exc_info=True)

async def background_manager(refId: str, url: str):
    try:
        logger.info(f"🚀 [Job Started] RefID: {refId} | URL: {url}")
        
        pdf_bytes, folder_name = load_pdf_and_name(url)
        
        chunks_map = locate_chunks(pdf_bytes=pdf_bytes, debug=False)
        start_chunk_page = [v for k, v in chunks_map.items() if k != "last_page"]
        
        logger.info(f"[{folder_name}] Structure detected. Found {len(start_chunk_page)-1} chunks to process.")

        tasks = []
        for i in range(len(start_chunk_page) - 1):
            start_page = start_chunk_page[i]
            end_page = start_chunk_page[i + 1]
            if start_page is None or end_page is None: continue

            task = process_and_save_chunk(
                chunk_idx=i,
                start_page=start_page,
                end_page=end_page,
                pdf_bytes=pdf_bytes,
                fileName=folder_name,
                start_chunk_page=start_chunk_page
            )
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"[{folder_name}] 🎉 All tasks finished successfully!")
        else:
            logger.warning(f"[{folder_name}] No tasks created.")
            
    except Exception as e:
        logger.error(f"Background Task Global Failed for {url}: {e}", exc_info=True)

@app.post("/api/curriculum/local-save")
async def extract_curr_local(body: ChunkRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(background_manager, body.refId, body.url)
    
    logger.info(f"Accepted request for {body.url} (Ref: {body.refId})")
    
    return {
        "status": 200,
        "message": "Processing started. Check logs/app.log for progress."
    }