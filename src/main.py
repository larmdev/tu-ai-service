from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
import json
import asyncio
import httpx
from dotenv import load_dotenv

from function.fn_gemini import call_openrouter_pdf
from function.fn_slice_page_pdf import slice_pdf_pages
from function.fn_pdf_to_byte import to_pdf_bytes
from function.fn_chunk_number import locate_chunks
from function.fn_pdf_from_url import load_pdf_from_url
from function.fn_pdf_text_table import text_with_tables
from function.fn_concat_pdf_bytes import concat_pdf_bytes
from function.fn_find_fisrt_page_non_empty import find_first_page_non_empty



load_dotenv()

OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")
CALLBACK_URL = os.getenv("CALLBACK_URL")

app = FastAPI()

from pydantic import BaseModel
from typing import Optional
class ChunkRequest(BaseModel):
    refId: str
    url: str
    fileName: Optional[str] = None


async def process_single_chunk(chunk_idx, start_page, end_page, pdf_bytes, refId, fileName, start_chunk_page):
    try:
        # if chunk_idx != 0:
        #     return

        if chunk_idx == 4 :
            return "chunk 4"
        start_page = start_chunk_page[chunk_idx]
        end_page = start_chunk_page[chunk_idx + 1]
        
        if start_page is None or end_page is None :
            return "no start/end page"
        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )
        
        if chunk_idx == 0:
            number_first_have_text = find_first_page_non_empty(pdf_bytes=pdf_bytes)
            chunk_pdf_bytes2 = slice_pdf_pages(pdf_bytes=pdf_bytes,start_page=number_first_have_text,end_page=number_first_have_text)
            chunk_pdf_bytes = concat_pdf_bytes(chunk_pdf_bytes2,chunk_pdf_bytes)

        text = None

        if chunk_idx == 0 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 1 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk2 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 2 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk3 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 3 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk4_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 5 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk5_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            # text = text_with_tables(chunk_pdf_bytes)
            # chunk_pdf_bytes = None

        elif chunk_idx == 6 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk6_1_1 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 7 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk7 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 8 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk8 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif chunk_idx == 9 and start_page is not None and end_page is not None:
            from fn_chunk.fn_chunk9 import schema_prompt
            schema, prompt, master_schema = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        data1 = await asyncio.to_thread (call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
            engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
            temperature=0.00,
        )

        if chunk_idx == 0:
            from regex.fn_clean1 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        if chunk_idx == 1:
            from regex.fn_clean2 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        if chunk_idx == 2:
            from regex.fn_clean3 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        if chunk_idx == 3 :
            from fn_chunk.fn_chunk4_1_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
            data2 = await asyncio.to_thread (call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )

            from fn_chunk.fn_chunk4_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

            start_page = start_chunk_page[chunk_idx+1]
            end_page = start_chunk_page[chunk_idx+2]
            chunk_pdf_bytes = slice_pdf_pages(
                pdf_bytes=pdf_bytes,
                start_page=start_page,
                end_page=end_page
            )

            data3 = await asyncio.to_thread(call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )

            from regex.fn_clean4 import clean
            data1 = clean (master_schema=master_schema,data1=data1,data2=data2,data3=data3)

        if chunk_idx == 5 :
            from fn_chunk.fn_chunk5_1_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
            text = text_with_tables(chunk_pdf_bytes)
            chunk_pdf_bytes2 = None
            data2 = await asyncio.to_thread(call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes2,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )
            text=None

            from fn_chunk.fn_chunk5_1_3 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
            data3 = await asyncio.to_thread (call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )

            from regex.fn_clean5 import clean
            data1 = clean (master_schema=master_schema,data1=data1,data2=data2,data3=data3)

        if chunk_idx == 6 :
            from fn_chunk.fn_chunk6_1_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)
            data2 = await asyncio.to_thread (call_openrouter_pdf,api_key=OPEN_ROUTER_KEY,model=MODEL,prompt=prompt,schema=schema,pdf_bytes=chunk_pdf_bytes,text = text,
                engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
                temperature=0.00,
            )

            from regex.fn_clean6 import clean
            data1 = clean (master_schema=master_schema,data1=data1,data2=data2)

        if chunk_idx == 7:
            from regex.fn_clean7 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        if chunk_idx == 8:
            from regex.fn_clean8 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        if chunk_idx == 9:
            from regex.fn_clean9 import clean
            data1 = clean (master_schema=master_schema,data1=data1)

        
        if chunk_idx >= 4 :
            plusnum = 0
        else :
            plusnum = 1

        section = str(chunk_idx + plusnum)

        payload = {
            "refId": refId,
            "fileName": fileName,
            "chunk": f"chunk{section}",
            "data": data1
        }

        # ยิง Callback
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{CALLBACK_URL}/g{section}", json=payload, timeout=60.0)
            print(f"Callback Chunk {section} Status: {resp.status_code}")

    except Exception as e:
        print(f"Error processing chunk {chunk_idx+1}: {e}")

async def background_manager(body: ChunkRequest, pdf_bytes: bytes):

    start_chunk_page = [v for k, v in locate_chunks(pdf_bytes=pdf_bytes, debug=False).items() if k != "last_page"]
    tasks = []

    # วนลูปสร้าง Task
    for i in range(len(start_chunk_page)-1):
        start_page = start_chunk_page[i]
        end_page = start_chunk_page[i + 1]

        if start_page is None or end_page is None:
            continue

        # สร้าง Task รอไว้ (ยังไม่ทำทันที)
        task = process_single_chunk(
            chunk_idx=i,
            start_page=start_page,
            end_page=end_page,
            pdf_bytes=pdf_bytes,
            refId=body.refId,
            fileName=body.fileName,
            start_chunk_page=start_chunk_page
        )
        tasks.append(task)

    # สั่งให้ทุก Task ทำงานพร้อมกัน
    if tasks:
        await asyncio.gather(*tasks)

# @app.post("/api/curriculum/file")
# async def extract_curr(body: ChunkRequest, background_tasks: BackgroundTasks):
#     # โหลด PDF
#     try:
#         pdf_bytes = load_pdf_from_url(body.url)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Cannot load PDF: {str(e)}")

#     # ทำงาน Background
#     background_tasks.add_task(background_manager, body, pdf_bytes)

#     # ตอบกลับทันที
#     return {
#         "status": 200,
#         "message": "Success. Processing started in background."
#     }

async def background_manager_with_download(body: ChunkRequest):
    try:
        pdf_bytes = load_pdf_from_url(body.url)
        await background_manager(body, pdf_bytes)
    except Exception as e:
        print(f"Background error: {e}")


@app.post("/api/curriculum/file")
async def extract_curr(body: ChunkRequest, background_tasks: BackgroundTasks):

    # ส่งไป background ทั้งก้อน (รวม download)
    background_tasks.add_task(background_manager_with_download, body)

    # ตอบกลับทันที (ไม่รออะไรเลย)
    return {
        "status": 200,
        "message": "Success. Processing started in background."
    }

@app.get("/api/env")
async def env():
    return {
        "OPEN_ROUTER_KEY": OPEN_ROUTER_KEY,
        "MODEL": MODEL,
        "CALLBACK_URL": CALLBACK_URL
    }

@app.get("/api/msg")
async def msg():
    return {
        "status": 200,
        "message": "API is running."
    }

