from src.fn_gemini import call_openrouter_pdf
from src.fn_slice_page_pdf import slice_pdf_pages
from src.fn_pdf_to_byte import to_pdf_bytes
from src.fn_chunk_number import locate_chunks
import os
import json

import io
import re
from typing import Any, Dict
from pathlib import Path

OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")

def reorder_by_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    props = schema.get("properties", {})
    ordered: Dict[str, Any] = {}

    for k in props.keys():           # เรียงตามลำดับใน schema["properties"]
        ordered[k] = data.get(k, None)

    return ordered


from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    if not pdf_bytes.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Not a real PDF")
    start_chunk_page = [v for k, v in locate_chunks(pdf_bytes= pdf_bytes, debug= False).items() if k not in ( "last_page")]
    
    ### รอลบ
    start_chunk_page = [x if i == 1 or i == 0 else None for i, x in enumerate(start_chunk_page)]

    print(start_chunk_page)
    for i in range(len(start_chunk_page)-1) :
        start_page = start_chunk_page[i]
        end_page = start_chunk_page[i + 1]

        print("                -------------             ")
        
        print("i =",i,"->",start_page,"and",end_page)

        if start_page is None or end_page is None:
            continue

        chunk_pdf_bytes = slice_pdf_pages(
            pdf_bytes=pdf_bytes,
            start_page=start_page,
            end_page=end_page
        )

        if i == 0 and start_page is not None and end_page is not None:
            print("do 1")
            from src.fn_chunk1 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 1 and start_page is not None and end_page is not None:
            from src.fn_chunk2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 2 and start_page is not None and end_page is not None:
            from src.fn_chunk3 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 3 and start_page is not None and end_page is not None:
            from src.fn_chunk4 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 4 and start_page is not None and end_page is not None:
            from src.fn_chunk4_2 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 5 and start_page is not None and end_page is not None:
            from src.fn_chunk5 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 6 and start_page is not None and end_page is not None:
            from src.fn_chunk6 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 7 and start_page is not None and end_page is not None:
            from src.fn_chunk7 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 8 and start_page is not None and end_page is not None:
            from src.fn_chunk8 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        elif i == 9 and start_page is not None and end_page is not None:
            from src.fn_chunk9 import schema_prompt
            schema, prompt = schema_prompt(chunk_pdf_bytes=chunk_pdf_bytes)

        data = call_openrouter_pdf(
            api_key=OPEN_ROUTER_KEY,
            model=MODEL,
            prompt=prompt,
            schema=schema,
            pdf_bytes=pdf_bytes,
            engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
            temperature=0.0,
        )
        print("                -------------             ")
        data = reorder_by_schema(data, schema)
        print(json.dumps(data, ensure_ascii=False, indent=2))

    return {"filename": data}


















# ----------------------------------------------------------------------
# OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
# MODEL = os.getenv("MODEL")

### pdf from .....
# pdf_bytes = to_pdf_bytes(pdf)


### print(chunk_page) -> {'chunk1': 2, 'chunk2': 5, 'chunk3': 6, 'chunk4': 10, 'chunk4_2': 24, 'chunk5': 60, 'chunk6': 64, 'chunk7': 68, 'chunk8': 69, 'chunk9': 70, 'end_chunk': 73, 'last_page': 75}
# start_chunk_page = [1] + [v for k, v in locate_chunks(pdf_bytes= pdf_bytes, debug= False).items() if k not in ("chunk1", "last_page")]

# for i in range(len(start_chunk_page)-1) :
    # start_page = start_chunk_page[i]
    # end_page = start_chunk_page[i + 1]

#     chunk_pdf_bytes = slice_pdf_pages(
#         pdf_bytes=pdf_bytes,
#         start_page=start_page,
#         end_page=end_page
#     )

    # if i == 0 and start_page is not None and end_page is not None:
#         from fn_chunk1 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 1 and start_page is not None and end_page is not None:
#         from fn_chunk2 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 2 and start_page is not None and end_page is not None:
#         from fn_chunk3 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 3 and start_page is not None and end_page is not None:
#         from fn_chunk4 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 4 and start_page is not None and end_page is not None:
#         from fn_chunk4_2 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 5 and start_page is not None and end_page is not None:
#         from fn_chunk5 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 6 and start_page is not None and end_page is not None:
#         from fn_chunk6 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 7 and start_page is not None and end_page is not None:
#         from fn_chunk7 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 8 and start_page is not None and end_page is not None:
#         from fn_chunk8 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     elif i == 9 and start_page is not None and end_page is not None:
#         from fn_chunk9 import schema_prompt
#         schema, prompt = schema_prompt(pdf_bytes=chunk_pdf_bytes)

#     data = call_openrouter_pdf(
#         api_key=OPEN_ROUTER_KEY,
#         model=MODEL,
#         prompt=prompt,
#         schema=schema,
#         pdf_bytes=chunk_pdf_bytes,
#         engine="pdf-text", #"mistral-ocr" สำหรับรูปภาพ
#         temperature=0.0,
#     )