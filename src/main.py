from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import os
import json
import asyncio
import httpx
from dotenv import load_dotenv

from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_pdf_to_byte import to_pdf_bytes
from fn_chunk_number import locate_chunks
from fn_pdf_from_url import load_pdf_from_url



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

        # กำหนด schema & prompt
        if chunk_idx == 4 :
            return "ppp"

        schema, prompt = None, None
        if chunk_idx == 0:
            from fn_chunk1 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 1:
            from fn_chunk2 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 2:
            from fn_chunk3 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 3:
            from fn_chunk4_2 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 5:
            # กลับมาเริ่ม fn_chunk5 ตามที่คุณต้องการ
            from fn_chunk5 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 6:
            from fn_chunk6 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 7:
            from fn_chunk7 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 8:
            from fn_chunk8 import schema_prompt
            schema, prompt = schema_prompt()

        elif chunk_idx == 9:
            from fn_chunk9 import schema_prompt
            schema, prompt = schema_prompt()

        # ตัด PDF
        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        # extract data
        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=chunk_pdf_bytes,
            engine="pdf-text",
            temperature=0.00,
        )

        # if chunk_idx == 3:
        #     from fn_chunk4_2 import schema_prompt
        #     schema, prompt = schema_prompt()
        #     chunk_pdf_bytes = slice_pdf_pages(
        #         pdf_bytes=pdf_bytes,
        #         start_page=start_chunk_page[4],
        #         end_page=start_chunk_page[5]
        #     )
        #     data2 = call_openrouter_pdf(
        #         api_key=OPEN_ROUTER_KEY,
        #         model=MODEL,
        #         prompt=prompt,
        #         schema=schema,
        #         pdf_bytes=chunk_pdf_bytes,
        #         engine="pdf-text",
        #         temperature=0.00,
        #     )


        ####### regex 1-9
        
        if chunk_idx >= 4 :
            plusnum = 0
        else :
            plusnum = 1

        section = str(chunk_idx + plusnum)

        payload = {
            "refId": refId,
            "fileName": fileName,
            "chunk": f"chunk{section}",
            "data": data
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

@app.post("/api/curriculum/file")
async def extract_curr(body: ChunkRequest, background_tasks: BackgroundTasks):
    # โหลด PDF
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot load PDF: {str(e)}")

    # ทำงาน Background
    background_tasks.add_task(background_manager, body, pdf_bytes)

    # ตอบกลับทันที
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

