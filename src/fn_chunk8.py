def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF
        ❗ ห้ามอธิบาย
        ❗ ตอบเป็น JSON เท่านั้น ตาม schema

        หมวดที่ 8 การบริหารหลักสูตร การควบคุมคุณภาพ และการประกันคุณภาพ

        ให้ดึงข้อมูลต่อไปนี้:

        1. การวางแผนและพัฒนาหลักสูตร
        - หลักการ แนวคิด หรือกระบวนการพัฒนา

        2. การควบคุมคุณภาพหลักสูตร
        - เกณฑ์มาตรฐาน
        - การบริหารจัดการหลักสูตร
        - รายละเอียดการควบคุมคุณภาพ

        3. ระบบประกันคุณภาพหลักสูตร
        - ภายใน / ภายนอก

        4. การปรับปรุงหลักสูตรประจำปี

        5. ตัวชี้วัดคุณภาพหลักสูตรประจำปี

        6. การประเมินความต้องการของผู้มีส่วนได้ส่วนเสีย

        7. ผลลัพธ์การเรียนรู้ของผู้เรียน (PLO / CLO)

        8. การติดตามคุณภาพอาจารย์ผู้รับผิดชอบหลักสูตร

        9. การควบคุมคุณภาพด้านจำนวนนักศึกษา
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

curriculumPlanningAndDevelopment

curriculumQualityControl
standardCriteria
curriculumManagement
details

curriculumQualityAssurance

annualCurriculumImprovement

annualCurriculumQualityIndicators

stakeholderNeeds

learningOutcomeResults

courseLecturerQuality

studentCountQuality
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {
                "type": ["string", "null"]
            },
            "curriculumPlanningAndDevelopment": {
                "type": ["string", "null"]
            },
            "curriculumQualityControl": {
                "type": ["object", "null"],
                "properties": {
                    "standardCriteria": {
                        "type": ["string", "null"]
                    },
                    "curriculumManagement": {
                        "type": ["string", "null"]
                    },
                    "details": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "standardCriteria",
                    "curriculumManagement",
                    "details"
                ],
                "additionalProperties": False
            },
            "curriculumQualityAssurance": {
                "type": ["string", "null"]
            },
            "annualCurriculumImprovement": {
                "type": ["string", "null"]
            },
            "annualCurriculumQualityIndicators": {
                "type": ["string", "null"]
            },
            "stakeholderNeeds": {
                "type": ["string", "null"]
            },
            "learningOutcomeResults": {
                "type": ["string", "null"]
            },
            "courseLecturerQuality": {
                "type": ["string", "null"]
            },
            "studentCountQuality": {
                "type": ["string", "null"]
            }
        },
        "additionalProperties": False
    }

    return schema, prompt
