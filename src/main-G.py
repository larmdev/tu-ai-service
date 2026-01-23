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


class ChunkRequest(BaseModel):
    refId: str
    url: str
    fileName: Optional[str] = None

# 1. ฟังก์ชันย่อยสำหรับประมวลผล 1 Chunk และยิง Callback (Worker)
async def process_single_chunk(chunk_idx, start_page, end_page, pdf_bytes, refId, fileName):
    try:
        # เลือก Schema ตาม Index (เหมือน Logic เดิมของคุณ)
        schema, prompt = None, None
        if chunk_idx == 0:
            from fn_chunk1 import schema_prompt
            schema, prompt = schema_prompt()
        elif chunk_idx == 1:
            from fn_chunk2 import schema_prompt
            schema, prompt = schema_prompt()
        # ... เพิ่มเงื่อนไขสำหรับ chunk อื่นๆ ...
        
        if not prompt: 
            return # ถ้าไม่มี prompt ให้ข้าม

        # ตัด PDF
        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        # เรียก AI
        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=chunk_pdf_bytes,
            engine="pdf-text",
            temperature=0.00,
        )

        # เตรียม Payload ส่งกลับ
        payload = {
            "refId": refId,
            "fileName": fileName,
            "chunk": f"chunk{chunk_idx + 1}", # เช่น chunk1, chunk2
            "data": data
        }

        # ยิง Callback กลับไป (Fire and Forget)
        async with httpx.AsyncClient() as client:
            resp = await client.post(CALLBACK_URL, json=payload, timeout=60.0)
            print(f"Callback Chunk {chunk_idx+1} Status: {resp.status_code}")

    except Exception as e:
        print(f"Error processing chunk {chunk_idx+1}: {e}")

# 2. ฟังก์ชันหลักสำหรับแจกงาน (Manager)
async def background_manager(body: ChunkRequest, pdf_bytes: bytes):
    # หาตำแหน่งหน้า
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
            fileName=body.fileName
        )
        tasks.append(task)

    # สั่งให้ทุก Task ทำงานพร้อมกัน (Parallel)
    if tasks:
        await asyncio.gather(*tasks)

# 3. API Endpoint
@app.post("/api/curriculum/file")
async def extract_curr(body: ChunkRequest, background_tasks: BackgroundTasks):
    try:
        # โหลด PDF มาเป็น bytes รอไว้ก่อนเลย (เพื่อให้แน่ใจว่าโหลดได้)
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        # ถ้าโหลดไม่ได้ ให้ Error กลับไปทันที 400
        raise HTTPException(status_code=400, detail=f"Cannot load PDF: {str(e)}")

    # --- ส่วนที่ 2: โยนงานเข้า Background ---
    # ส่ง pdf_bytes ที่โหลดแล้วเข้าไปด้วย จะได้ไม่ต้องโหลดซ้ำข้างใน
    background_tasks.add_task(background_manager, body, pdf_bytes)

    # --- ส่วนที่ 3: ตอบกลับทันที ---
    return {
        "status": 200,
        "message": "Success. Processing started in background."
    }


################
@app.post("/api/curriculum/file")
async def extract_curr(body: ChunkRequest):

    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    start_chunk_page = [v for k, v in locate_chunks(pdf_bytes= pdf_bytes, debug= False).items() if k not in ( "last_page")]

    for i in range(len(start_chunk_page)-1) :
        start_page = start_chunk_page[i]
        end_page = start_chunk_page[i + 1]

        if start_page is None or end_page is None :
            continue

        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        if i == 0 :
            from fn_chunk1 import schema_prompt

        elif i == 1 :
            from fn_chunk2 import schema_prompt
            
        schema, prompt = schema_prompt()

        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=chunk_pdf_bytes,
            engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
            temperature=0.00,
        )

        return {
            "refId": body.refId,
            "fileName": body.fileName,
            "chunk": "chunk1",
            "data": data
        }
