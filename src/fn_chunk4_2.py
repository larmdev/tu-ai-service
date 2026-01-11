
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

    2course (เก็บรายวิชาทั้งหมดที่มี)
        2course_type รายวิชานี้อยู่ในหมวดใดของโครงสร้างหลักสูตร(ค่าต้องอยู่ใน detail_credit["main"]["value_main"] เท่านั้น และเอามาแค่ค่าเท่านั้นไม่ต้องเอาลำดับมา)
        2sub_course_type รายวิชานี้อยู่ในหมวดย่อย ของหมวดหลัก ใดของโครงสร้างหลักสูตร (ค่าต้องอยู่ใน detail_credit["main"]["detail_main"]["value_sub_main"] ที่อยู่ใน detail_credit["main"]["value_main"] เดียวกันเท่านั้น ส่วนมาก "value_main" มีอยู่ลำดับต้นเช่น 1. 2. "value_sub_main" จะเป็นหัวข้อย่อยเช่น 1.1  2.2 2.3 และเอามาแค่ค่าเท่านั้นไม่ต้องเอาลำดับมา)
        2thai_abv ชื่อรหัสวิชาย่อ ภาษาไทย (format ให้เป็น ตัวย่อภาษาไทย. เลข ในกรณีที่ตัวอักษรกับภาษาแยกกันชัดเจน หากแยกกันไม่ชัดเจนให้ตัวติดกันให้หมด)
        2th_name ชื่อวิชาเต็ม ภาษาไทย
        2credit จำนวนหน่วยกิตเต็มของรายวิชานั้น (เอามาแค่ตัวเลข)
        2credit_detail รายละเอียดของหน่วยกิตรายวิชา (ส่วนมากจะเป็น (เลข-เลข-เลข) บางกรณีอาจเป็น (มากกว่า เลข ชั่วโมง) format ที่ให้เก็บให้เติม '()'ครอบทั้งหมดด้วยหากไม่มี)
        2eng_abv ชื่อรหัสวิชาย่อ ภาษาอังกฤษ (format ให้เป็น ตัวย่อภาษาอังกฤษ เลข ในกรณีที่ตัวอักษรกับภาษาแยกกันชัดเจน หากแยกกันไม่ชัดเจนให้ตัวติดกันให้หมด)
        2eng_name ชื่อวิชาเต็ม ภาษาอังกฤษ
    """


    schema = {
        "type": "object",
        "properties": {
            "2course": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "2course_type": {"type": ["string", "null"]},
                        "2sub_course_type": {"type": ["string", "null"]},
                        "2thai_abv": {"type": ["string", "null"]},
                        "2eng_abv": {"type": ["string", "null"]},
                        "2th_name": {"type": ["string", "null"]},
                        "2eng_name": {"type": ["string", "null"]},
                        "2credit": {"type": ["number", "null"]},
                        "2credit_detail": {"type": ["string", "null"]},
                        "2thai_desc": {"type": ["string", "null"]},
                        "2eng_desc": {"type": ["string", "null"]},
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