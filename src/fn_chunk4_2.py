def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจาก อธิบายรายวิชา

courses
  sequence null
  courseCodeTh รหัสวิชาภาษาไทย
  courseCodeEn รหัสวิชาภาษาอังกฤษ
  courseNameTh ชื่อวิชาภาษาไทยเต็ม
  courseNameEn ชื่อวิชาภาษาอังกฤษเต็ม
  courseDescriptionTh คำอธิบายรายวิชาภาษาไทย (เอาเรื่อง วิชาบังคับก่อน ด้วยแต่ไม่เอาเรื่องผลลัพธ์การเรียนรู้)
  courseDescriptionEn คำอธิบายรายวิชาภาษาอังกฤษ (เอาเรื่อง Prerequisite: ด้วย)
  credits หน่วยกิต (จะเป็นเลขเดี่ยวๆ)
  lecturePracticeSelfStudy รายละเอียดหน่วยกิต (จะเป็นข้อความทั้งหมดในวงเล็บหลังหน่วยกิตเช่น 2-2-5 หรือ 500ชั่วโมง)
    """

    schema = {
        "type": "object",
        "properties": {
            "courses": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "null"},
                        "courseCodeTh": {"type": ["string", "null"]},
                        "courseCodeEn": {"type": ["string", "null"]},
                        "courseNameTh": {"type": ["string", "null"]},
                        "courseNameEn": {"type": ["string", "null"]},
                        "credits": {"type": ["integer", "null"]},
                        "courseDescriptionTh": {"type": ["string", "null"]},
                        "courseDescriptionEn": {"type": ["string", "null"]},
                        "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                    },
                    "required": ["sequence"],
                },
            },
        },
    }

    return schema, prompt
