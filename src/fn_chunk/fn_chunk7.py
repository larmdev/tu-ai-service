def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 7

curriculumId

learningAssessment การประเมินผลการเรียนรู้ของนักศึกษา (เอาเนื้อหาในหัวข้อนี้มาทั้งหมด)

standardVerificationProcess กระบวนการทวนสอบมาตรฐานผลสัมฤทธิ์ของนักศึกษา (เอาเนื้อหาในหัวข้อนี้มาทั้งหมด)

appealProcess การอุทธรณ์ผลการศึกษาของนักศึกษา (เอาเนื้อหาในหัวข้อนี้มาทั้งหมด)

graduationCriteria เกณฑ์การสําเร็จการศึกษาตามหลักสูตร (เอาเนื้อหาในหัวข้อนี้มาทั้งหมด)
    """

    schema = {
        "type": "object",
        "properties": {
            "learningAssessment": {
                "type": ["string", "null"]
            },
            "standardVerificationProcess": {
                "type": ["string", "null"]
            },
            "appealProcess": {
                "type": ["string", "null"]
            },
            "graduationCriteria": {
                "type": ["string", "null"]
            }
        },
        "additionalProperties": False
    }

    master_schema = {
        "type": "object",
        "properties": {
            "learningAssessment": {
                "type": ["string", "null"]
            },
            "standardVerificationProcess": {
                "type": ["string", "null"]
            },
            "appealProcess": {
                "type": ["string", "null"]
            },
            "graduationCriteria": {
                "type": ["string", "null"]
            }
        },
        "additionalProperties": False
    }

    return schema, prompt, master_schema
