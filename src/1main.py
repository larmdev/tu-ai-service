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
from function.fn_pdf_text_table import text_with_tables

# -------------------------
# Logging
# -------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# -------------------------
# ENV
# -------------------------
OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")

DEFAULT_LOCAL_PATH = os.path.expanduser("~/Desktop/pimdej/curriculum_tu/data")
TARGET_BASE_DIR = os.getenv("OUTPUT_DIR", DEFAULT_LOCAL_PATH)

# -------------------------
# FastAPI
# -------------------------
app = FastAPI()

class ChunkRequest(BaseModel):
    refId: str
    url: str

# -------------------------
# Helpers
# -------------------------
def fix_utf8(text: str) -> str:
    if not text:
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except Exception:
        return text

def get_google_drive_direct_link(url: str) -> Tuple[str, Optional[str]]:
    patterns = [
        r"drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)",
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

def load_pdf_and_name(url: str) -> Tuple[bytes, str]:
    logger.info(f"Start downloading: {url}")
    direct_url, file_id = get_google_drive_direct_link(url)

    response = requests.get(direct_url)
    response.raise_for_status()

    filename = None
    if "content-disposition" in response.headers:
        cd = response.headers["content-disposition"]
        fname_match = re.search(r'filename="?([^"]+)"?', cd)
        if fname_match:
            filename = fname_match.group(1)
        elif "filename*" in cd:
            fname_match = re.search(r"filename\*=UTF-8''(.+)", cd)
            if fname_match:
                filename = urllib.parse.unquote(fname_match.group(1))

    if not filename:
        if file_id:
            filename = f"gdrive_{file_id}"
        else:
            filename = url.split("/")[-1].split("?")[0] or "unknown_file"

    filename = fix_utf8(filename)

    # remove .pdf
    folder_name = filename[:-4] if filename.lower().endswith(".pdf") else filename
    folder_name = re.sub(r'[<>:"/\\|?*]', "_", folder_name)

    logger.info(f"Download complete. Resolved Name: {folder_name}")
    return response.content, folder_name


# -------------------------
# ✅ Async Wrapper (IMPORTANT)
# -------------------------
async def call_openrouter_pdf_async(
    semaphore: asyncio.Semaphore,
    *,
    api_key: str,
    model: str,
    prompt: str,
    schema: Dict[str, Any],
    pdf_bytes: Optional[bytes] = None,
    text: Optional[str] = None,
    engine: str = "pdf-text",
    temperature: float = 0.0,
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    """
    call_openrouter_pdf เป็น sync (requests) -> ห้าม await ตรงๆ
    ใช้ asyncio.to_thread + semaphore เพื่อให้ทำงานพร้อมกันแบบปลอดภัย
    """
    async with semaphore:
        return await asyncio.to_thread(
            call_openrouter_pdf,
            api_key=api_key,
            model=model,
            prompt=prompt,
            schema=schema,
            pdf_bytes=pdf_bytes,
            text=text,
            engine=engine,
            temperature=temperature,
            timeout=timeout,
        )


# -------------------------
# Chunk Worker
# -------------------------
async def process_and_save_chunk(
    *,
    chunk_idx: int,
    pdf_bytes: bytes,
    fileName: str,
    start_chunk_page: List[Optional[int]],
    semaphore: asyncio.Semaphore,
):
    section_str = str(chunk_idx)

    try:
        # ถ้าคุณอยาก skip chunk 4 เหมือนเดิม
        if chunk_idx == 4:
            logger.info(f"[{fileName}] skip chunk 4")
            return

        start_page = start_chunk_page[chunk_idx]
        end_page = start_chunk_page[chunk_idx + 1]

        if start_page is None or end_page is None:
            logger.warning(f"[{fileName}] chunk {chunk_idx} has no start/end page")
            return

        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page,
        )

        text = None

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
