from fn_gemini import call_openrouter_pdf
from fn_slice_page_pdf import slice_pdf_pages
from fn_pdf_to_byte import to_pdf_bytes
from fn_chunk_number import locate_chunks
import os
import json

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
from typing import Any, Dict
from pathlib import Path

PDF_URL = "https://drive.google.com/file/d/1Xlsqq3uIACYUSGZYfpewhW33DtjgKc4U/edit"

load_dotenv()
drive_url = os.getenv("DRIVE_URL")
sa_path = "service_account.json"
OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
MODEL = os.getenv("MODEL")
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

file_id = _extract_file_id_from_drive_url(PDF_URL)
pdf_bytes = download_drive_pdf_bytes(drive, file_id)



def reorder_by_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    props = schema.get("properties", {})
    ordered: Dict[str, Any] = {}

    for k in props.keys():           # เรียงตามลำดับใน schema["properties"]
        ordered[k] = data.get(k, None)

    return ordered


pdf_bytes = slice_pdf_pages(pdf_bytes=pdf_bytes,start_page=1,end_page=9)

schema = {
    "type": "object",
    "properties": {
        "curr_id": {"type": ["string", "null"]},
        "curr_name_th": {"type": ["string", "null"]},
        "curr_name_en": {"type": ["string", "null"]},
        "degree_full_th": {"type": ["string", "null"]},
        "degree_full_en": {"type": ["string", "null"]},
        "degree_abr_th": {"type": ["string", "null"]},
        "degree_abr_en": {"type": ["string", "null"]},
        "curr_category_id": {"type": ["string", "null"]},
        "curr_type_id": {"type": ["string", "null"]},
        "lang_id": {"type": ["string", "null"]},

        "mou": {"type": ["string", "null"]},
        "first_open_semester": {"type": ["integer", "null"]},
        "first_open_year": {"type": ["integer", "null"]},
        "careers": {"type": ["string", "null"]},
        "campus_id": {"type": ["string", "null"]},
        "expense_type": {"type": ["string", "null"]},
        "student_nation_id": {"type": ["string", "null"]},
        "qualification_collegian": {"type": ["string", "null"]},

        "plo": {
            "type": ["array", "null"],  # อนุญาตให้ทั้งก้อนเป็น null ได้
            "items": {
                "type": "object",
                "properties": {
                    "type_plo": {"type": ["string", "null"]},
                    "num_plo": {"type": ["integer", "null"]},
                    "detail_plo": {"type": ["string", "null"]},
                },
                "additionalProperties": False,
                # ถ้าอยากให้แต่ละ item ต้องมีครบ 3 key เสมอ (ไม่เจอให้ null) ก็ใส่ required
                "required": ["type_plo", "num_plo", "detail_plo"],
            },
        },
    },
    "additionalProperties": False,
    "required" : []
}

prompt = (
    """
    จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
    หมวดที่ 1 จะมี  curr_id รหัสหลักสูตร curr_name_th ชื่อหลักสูตรภาษาไทย curr_name_en ชื่อหลักสูตรภาษาอังกฤษ	degree_full_th ชื่อปริญญาและสาขาวิชาภาษาไทยชื่อเต็ม degree_full_en ชื่อปริญญาและสาขาวิชาภาษาอังกฤษชื่อเต็ม degree_abr_th ชื่อปริญญาและสาขาวิชาภาษาไทยชื่อย่อ degree_abr_en ชื่อปริญญาและสาขาวิชาภาษาอังกฤษชื่อย่อ 
    curr_category_id รูปแบบ จาก รูปแบบของหลักสูตร หมวดที่เจอคำคล้ายๆว่า 'หลักสูตรระดับปริญญาตรี 4 ปี หรือต่อเนื่อง' (เอามาเฉพาะค่าที่ถูกเลือก) curr_type_id ประเภทของหลักสูตร จาก รูปแบบของหลักสูตร (เอามาเฉพาะค่าที่ถูกเลือก) lang_id ภาษาที่ใช้ จาก รูปแบบของหลักสูตร หมวดที่เจอคำคล้ายๆว่า 'จัดการศึกษาเป็นภาษาไทย' (เอามาเฉพาะค่าที่ถูกเลือก) mou ความร่วมมือกับสถาบันอื่น จาก รูปแบบของหลักสูตร เป็นหมวดที่เจอคำคล้ายๆว่า 'เป็นหลักสูตรของสถาบันโดยเฉพาะ'(เอามาเฉพาะค่าที่ถูกเลือก) first_open_semester สถานภาพของหลักสูตรและการพิจารณาอนุมัติ/เห็นชอบหลักสูตร จาก รูปแบบของหลักสูตร ให้เอาเลขภาคการศึกษาที่เปิดสอนมาใส่ first_open_year สถานภาพของหลักสูตรและการพิจารณาอนุมัติ/เห็นชอบหลักสูตร จาก รูปแบบของหลักสูตร ให้เอาเลขปีการศึกษาที่เปิดสอนมาใส่ 
    careers อาชีพที่สามารถประกอบได้หลังสำเร็จการศึกษา จาก รูปแบบของหลักสูตร (ไม่เอาลำดับข้อ หากมีหลายตัวอยากให้ใช้ ,) campus_id สถานที่จัดการเรียนการสอน จาก รูปแบบของหลักสูตร (เอามาเฉพาะค่าที่ถูกเลือก หากมีหลายตัวอยากให้ใช้ ,) expense_type ประเภทโครงการ จากประเภทโครงการ จากรูปแบบ 
    หมวดที่ 2 student_nation_id การรับเข้าศึกษา (เอามาเฉพาะค่าที่ถูกเลือก) qualification_collegian คุณสมบัติของผู้เข้าศึกษา (เอามาแค่เฉพาะเนื้อหาในเกณฑ์ที่เป็นข้อๆ ไม่เอาอักษรพิเศษ ไม่เอาลำดับข้อ หากมีหลายข้อให้ใช้ , )

    หมวดที่ 3 type_plo ใน ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เป็นเกณฑ์ภาษาอังกฤษที่มีลำดับ เช่น plo1 plo2 k2 s2 e1 c1 เอามาแค่ตัวอักษร) num_plo ใน ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เป็นเกณฑ์ภาษาอังกฤษที่มีลำดับ เช่น plo1 plo2 k2 s2 e1 c1 เอามาแค่ตัวเลข) detail_plo ใน ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เป็นเกณฑ์ภาษาอังกฤษที่มีลำดับ เช่น PLO 1 PLO 2 K2 S2 E1 C1 เอามาแค่คำอธิบายของเกณฑ์นั้น)
    """
)


# 1) FREE text mode
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


# ✅ เขียนไฟล์ลง data/name.json
out_dir = Path("data")
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "name.json"   # เปลี่ยนชื่อไฟล์ได้
with out_path.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("[OK] wrote:", out_path.resolve())
















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