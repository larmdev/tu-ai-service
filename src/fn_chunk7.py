def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF
        ❗ ห้ามอธิบาย
        ❗ ตอบเป็น JSON เท่านั้น ตาม schema

        หมวดที่ 7 การประเมินผลและการสำเร็จการศึกษา

        ให้ดึงข้อมูลต่อไปนี้:

        1. การประเมินผลการเรียนรู้ของนักศึกษา
        - วิธีการประเมิน (เช่น สอบ รายงาน โครงงาน ฯลฯ)

        2. กระบวนการทวนสอบมาตรฐานผลสัมฤทธิ์
        - หน่วยงานหรือคณะกรรมการที่เกี่ยวข้อง

        3. กระบวนการอุทธรณ์ผลการศึกษา
        - เงื่อนไขและระยะเวลา

        4. เกณฑ์การสำเร็จการศึกษา
        - หน่วยกิต
        - รายวิชาบังคับ
        - คุณลักษณะหรือเงื่อนไขอื่น ๆ
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 7

curriculumId

learningAssessment การประเมินผลการเรียนรู้ของนักศึกษา

standardVerificationProcess กระบวนการทวนสอบมาตรฐานผลสัมฤทธิ์ของนักศึกษา

appealProcess การอุทธรณ์ผลการศึกษาของนักศึกษา

graduationCriteria เกณฑ์การสําเร็จการศึกษาตามหลักสูตร
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {
                "type": ["string", "null"]
            },
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

    return schema, prompt
