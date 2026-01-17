from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import Optional
import json
import os
from dotenv import load_dotenv

from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_chunk_number import locate_chunks
from fn_pdf_from_url import load_pdf_from_url

load_dotenv()

OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")

app = FastAPI()


def reorder_by_schema(data, schema):
    props = schema.get("properties", {})
    return {k: data.get(k) for k in props.keys()}


@app.post("/upload-pdf")
async def upload_pdf(
    file: Optional[UploadFile] = File(None),
    pdf_url: Optional[str] = Form(None),
):
    # -------------------------
    # 1) โหลด PDF เป็น bytes
    # -------------------------
    if file:
        pdf_bytes = await file.read()
    elif pdf_url:
        try:
            pdf_bytes = load_pdf_from_url(pdf_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either file or pdf_url"
        )

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Not a real PDF")

    # -------------------------
    # 2) หา chunk
    # -------------------------
    start_chunk_page = [
        v for k, v in locate_chunks(pdf_bytes=pdf_bytes, debug=False).items()
        if k != "last_page"
    ]

    # (เหมือนโค้ดเดิมของคุณ)
    start_chunk_page = [x if i in (0, 1) else None for i, x in enumerate(start_chunk_page)]

    results = {}

    # -------------------------
    # 3) วน chunk
    # -------------------------
    for i in range(len(start_chunk_page) - 1):
        start_page = start_chunk_page[i]
        end_page = start_chunk_page[i + 1]

        if start_page is None or end_page is None:
            continue

        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        # -------------------------
        # 4) เลือก schema + prompt
        # -------------------------
        if i == 0:
            from fn_chunk1 import schema_prompt
            chunk_name = "fn_chunk1"
        elif i == 1:
            from fn_chunk2 import schema_prompt
            chunk_name = "fn_chunk2"
        elif i == 2:
            from fn_chunk3 import schema_prompt
            chunk_name = "fn_chunk3"
        elif i == 3:
            from fn_chunk4 import schema_prompt
            chunk_name = "fn_chunk4"
        elif i == 4:
            from fn_chunk4_2 import schema_prompt
            chunk_name = "fn_chunk4_2"
        elif i == 5:
            from fn_chunk5 import schema_prompt
            chunk_name = "fn_chunk5"
        elif i == 6:
            from fn_chunk6 import schema_prompt
            chunk_name = "fn_chunk6"
        elif i == 7:
            from fn_chunk7 import schema_prompt
            chunk_name = "fn_chunk7"
        elif i == 8:
            from fn_chunk8 import schema_prompt
            chunk_name = "fn_chunk8"
        elif i == 9:
            from fn_chunk9 import schema_prompt
            chunk_name = "fn_chunk9"
        else:
            continue

        schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        # -------------------------
        # 5) เรียก OpenRouter
        # -------------------------
        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=pdf_bytes,
            engine="pdf-text",
            temperature=0.0,
        )

        data = reorder_by_schema(data, schema)
        results[chunk_name] = data

    return results
