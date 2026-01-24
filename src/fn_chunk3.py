def schema_prompt(chunk_pdf_bytes: bytes | None = None):

    prompt = """
        จากไฟล์ที่ extract มา (เรียงจากบนลงล่าง)
        ห้ามอธิบาย ห้ามตอบข้อความอื่น
        ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

        หมวดที่ 3

        1. educationalPhilosophy
        - จากหัวข้อ ปรัชญาการศึกษา
        - เอาข้อความทั้งหมด

        2. curriculumObjectives
        - จากหัวข้อ วัตถุประสงค์ของหลักสูตร
        - เอาทั้งหมด คงลำดับเดิม

        3. programLearningOutcomes
        - แยกตามแผนการศึกษา (เช่น แผนการศึกษาที่ 1, แผนการศึกษาที่ 2)
        - ในแต่ละแผน มีรายการ PLO

        PLO:
        - ploCode เช่น PLO1, PLO2
        - ploText คือข้อความอธิบาย PLO
        - subPlos คือ PLO ย่อย (ถ้ามี)

        subPlos:
        - subPloCode เช่น PLO1-1, PLO1-2
        - subPloText คือข้อความอธิบาย

        ถ้าไม่มีข้อมูล ให้ใช้ null

        ตรง ploCode ให้เริ่มด้วย PLO1, PLO2, .. PLOn ตามลำดับ
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

educationalPhilosophy

curriculumObjectives

programLearningOutcomes
  curriculumPlan
  plos
    ploCode
    ploText
    subPlos
      subPloCode
      subPloText
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": { "type": ["string", "null"] },

            "educationalPhilosophy": {
                "type": ["string", "null"]
            },
            "curriculumObjectives": {
                "type": ["string", "null"]
            },
            "programLearningOutcomes": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "curriculumPlan": { "type": ["string"] },
                        "plos": {
                            "type": ["array"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ploCode": { "type": ["string"] },
                                    "ploText": { "type": ["string"] },
                                    "subPlos": {
                                        "type": ["array", "null"],
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "subPloCode": { "type": ["string"] },
                                                "subPloText": { "type": ["string"] }
                                            },
                                            "required": ["subPloCode", "subPloText"],
                                            "additionalProperties": False
                                        }
                                    }
                                },
                                "required": ["ploCode", "ploText"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["curriculumPlan", "plos"],
                    "additionalProperties": False
                }
            }
        },
        "required": [],
        "additionalProperties": False
    }

    return schema, prompt
