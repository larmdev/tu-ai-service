
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

    course ###
    course_type ###
    sub_course_type ###
    thai_abv ###
    eng_abv ###
    th_name ###
    eng_name ###
    credit ###
    credit_detail ###
    thai_desc ###
    eng_desc ###
    """


    schema = {
        "type": "object",
        "properties": {
            "course": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "course_type": {"type": ["string", "null"]},
                        "sub_course_type": {"type": ["string", "null"]},
                        "thai_abv": {"type": ["string", "null"]},
                        "eng_abv": {"type": ["string", "null"]},
                        "th_name": {"type": ["string", "null"]},
                        "eng_name": {"type": ["string", "null"]},
                        "credit": {"type": ["number", "null"]},
                        "credit_detail": {"type": ["string", "null"]},
                        "thai_desc": {"type": ["string", "null"]},
                        "eng_desc": {"type": ["string", "null"]},
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
        },
        "required": [],
        "additionalProperties": False,
    }


    return schema, prompt