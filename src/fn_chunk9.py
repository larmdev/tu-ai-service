def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF
        ❗ ห้ามอธิบาย
        ❗ ตอบเป็น JSON เท่านั้น ตาม schema

        หมวดที่ 9 การประเมินผลหลักสูตร และการปรับปรุงหลักสูตร

        ให้ดึงข้อมูลดังนี้:

        1. การประเมินประสิทธิผลการจัดการเรียนการสอนรายวิชา
        2. การประเมินการจัดการเรียนการสอนของอาจารย์
        3. การประเมินหลักสูตรโดยรวม
        4. การประเมินผลการดำเนินงานตามรายละเอียดหลักสูตร
        5. การทบทวนผลการประเมินและการปรับปรุงหลักสูตร

        6. จุดแข็งของหลักสูตร
        - เรียงลำดับ
        - ระบุชื่อจุดแข็ง และรายละเอียด

        7. จุดอ่อนของหลักสูตร
        - เรียงลำดับ
        - ระบุชื่อจุดอ่อน และรายละเอียด
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

courseTeachingEffectiveness

teachingManagementEvaluation

overallCurriculumEvaluation

curriculumImplementationEvaluation

curriculumReviewAndImprovement

curriculumImprovementStrengths
sequence
name
detail

curriculumImprovementWeaknesses
sequence
name
detail
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {
                "type": ["string", "null"]
            },

            "courseTeachingEffectiveness": {
                "type": ["string", "null"]
            },
            "teachingManagementEvaluation": {
                "type": ["string", "null"]
            },
            "overallCurriculumEvaluation": {
                "type": ["string", "null"]
            },
            "curriculumImplementationEvaluation": {
                "type": ["string", "null"]
            },
            "curriculumReviewAndImprovement": {
                "type": ["string", "null"]
            },

            "curriculumImprovementStrengths": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {
                            "type": ["integer", "null"]
                        },
                        "name": {
                            "type": ["string", "null"]
                        },
                        "detail": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": ["sequence", "name", "detail"],
                    "additionalProperties": False
                }
            },

            "curriculumImprovementWeaknesses": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {
                            "type": ["integer", "null"]
                        },
                        "name": {
                            "type": ["string", "null"]
                        },
                        "detail": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": ["sequence", "name", "detail"],
                    "additionalProperties": False
                }
            }
        },
        "additionalProperties": False
    }

    return schema, prompt
