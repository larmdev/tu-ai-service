from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv
import os, json

from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_chunk_number import locate_chunks
from fn_pdf_from_url import load_pdf_from_url

load_dotenv()

OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")

app = FastAPI()

from pydantic import BaseModel
from typing import Optional

class ChunkRequest(BaseModel):
    refId: str
    url: str
    fileName: Optional[str] = None


def process_chunk(
    pdf_bytes: bytes,
    chunk_index: int,
    schema_prompt_fn
):
    chunk_pages = list(
        v for k, v in locate_chunks(pdf_bytes=pdf_bytes, debug=False).items()
        if k != "last_page"
    )

    start_page = chunk_pages[chunk_index]
    end_page = chunk_pages[chunk_index + 1]

    chunk_pdf_bytes = slice_pdf_pages(
        pdf_bytes=pdf_bytes,
        start_page=start_page,
        end_page=end_page
    )

    schema, prompt = schema_prompt_fn(chunk_pdf_bytes=chunk_pdf_bytes)

    data = call_openrouter_pdf(
        api_key=OPEN_ROUTER_KEY,
        model=MODEL,
        prompt=prompt,
        schema=schema,
        pdf_bytes=pdf_bytes,   # ❗ ใช้ pdf เต็ม เหมือนของเดิม
        engine="pdf-text",
        temperature=0.0,
    )

    return data

async def get_pdf_bytes(file: UploadFile | None, pdf_url: str | None) -> bytes:
    if file:
        pdf_bytes = await file.read()
    elif pdf_url:
        pdf_bytes = load_pdf_from_url(pdf_url)
    else:
        raise HTTPException(400, "ต้องส่ง file หรือ pdf_url")

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(400, "Not a valid PDF")

    return pdf_bytes

@app.post("/chunk-1")
async def chunk_1(body: ChunkRequest):
    
    from fn_chunk1 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=0,
        schema_prompt_fn=schema_prompt
    )

    ## callback-api

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk1",
        "data": data
    }


@app.post("/chunk-2")
async def chunk_2(body: ChunkRequest):
    
    from fn_chunk2 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=1,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk2",
        "data": data
    }


@app.post("/chunk-3")
async def chunk_3(body: ChunkRequest):

    from fn_chunk3 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=2,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk3",
        "data": data
    }


@app.post("/chunk-4")
async def chunk_4(body: ChunkRequest):

    from fn_chunk4 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=3,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk4",
        "data": data
    }

@app.post("/chunk-5")
async def chunk_5(body: ChunkRequest):

    from fn_chunk5 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=4,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk5",
        "data": data
    }

@app.post("/chunk-6")
async def chunk_6(body: ChunkRequest):

    from fn_chunk6 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=5,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk6",
        "data": data
    }

@app.post("/chunk-7")
async def chunk_7(body: ChunkRequest):

    from fn_chunk7 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=6,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk7",
        "data": data
    }

@app.post("/chunk-8")
async def chunk_8(body: ChunkRequest):

    from fn_chunk8 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=7,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk8",
        "data": data
    }


@app.post("/chunk-9")
async def chunk_9(body: ChunkRequest):

    from fn_chunk9 import schema_prompt
    try:
        pdf_bytes = load_pdf_from_url(body.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    data = process_chunk(
        pdf_bytes=pdf_bytes,
        chunk_index=8,
        schema_prompt_fn=schema_prompt
    )

    return {
        "refId": body.refId,
        "fileName": body.fileName,
        "chunk": "chunk9",
        "data": data
    }