def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 4

curriculumId null

จากหัวข้อ โครงสร้างหลักสูตร
minimumCurriculumCredits จำนวนหน่วยกิต ที่ต้องจดทะเบียบขั้นต่ำ
curriculumStructures
  courseGroup หมวดวิชาใหญ่
  courseCredits จำนวนหน่วยกิตของ หมวดวิชาใหญ่

courses
จากหัวข้อ รายวิชาและข้อกําหนดของหลักสูตร
  sequence null
  courseGroup หมวดรายวิชาใหญ่ (ต้องเป็นค่าที่อยู่ใน ourseGroup จาก curriculumStructures เท่านั้น)
  lecturePracticeSelfStudy
  courseCodeTh รหัสวิชา ภาษาไทย
  courseCodeEn รหัสวิชา ภาษาอังกฤษ
  courseNameTh ชื่อรายวิชา ภาษาไทย
  courseNameEn ชื่อรายวิชา ภาษาอังกฤษ
  credits หน่วยกิต (เป็นเลขเดี่ยวๆอยู่ด้านหลัง ชื่อวิชาภาษาไทย)



    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
            "courses": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "integer"},
                        "courseCodeTh": {"type": ["string", "null"]},
                        "courseCodeEn": {"type": ["string", "null"]},
                        "courseNameTh": {"type": ["string", "null"]},
                        "courseNameEn": {"type": ["string", "null"]},
                        "courseDescriptionTh": {"type": ["string", "null"]},
                        "courseDescriptionEn": {"type": ["string", "null"]},
                        "credits": {"type": ["integer", "null"]},
                        "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                        "courseGroup": {"type": ["string", "null"]},
                        "semester": {"type": ["integer", "null"]},
                        "academicYear": {"type": ["integer", "null"]},
                    },
                    "required": ["sequence"],
                },
            },
            "academicRequirements": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "integer"},
                        "title": {"type": "string"},
                        "detail": {"type": ["string", "null"]},
                    },
                    "required": ["sequence", "title"],
                },
            },
        },
        "additionalProperties": False,
    }

    return schema, prompt
