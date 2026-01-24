
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """
            จากเอกสาร PDF ที่ให้มา (เรียงจากบนลงล่าง)
            ห้ามตอบคำอธิบายใด ๆ
            ให้ตอบเป็น JSON อย่างเดียว และต้องตรงตาม schema ที่กำหนดเท่านั้น

            หมวดที่ 2 การรับเข้าศึกษา

            1. admissionType2
            - มาจากหัวข้อ "การรับเข้าศึกษา"
            - เป็นค่าเดียวที่ถูกเลือก
            - ใช้รูปแบบตัวพิมพ์เล็กและขีดกลาง เช่น
            - thai
            - international
            - thai-and-international

            2. admissionQualifications
            - จากหัวข้อ "คุณสมบัติของผู้เข้าศึกษา"
            - รวมทุกข้อ
            - หากมีหลายข้อ ให้คั่นด้วย ","

            3. admissionSelectionProcess
            - จากหัวข้อ "การคัดเลือกผู้เข้าศึกษา"

            4. studentsPerYear
            - จากข้อความ "ในแต่ละปีการศึกษาจะรับนักศึกษาปีละ"
            - เอาเฉพาะตัวเลข

            5. studentAdmissionPlans
            - มาจากตาราง "แผนการรับนักศึกษาและผู้สำเร็จการศึกษาในระยะ 5 ปี"
            - แต่ละตาราง = 1 plan
            - rows ต้องเรียงตามลำดับที่ปรากฏในตาราง
            - years เป็น object โดยใช้ปีการศึกษาเป็น key
            - หากค่าเป็น "-" หรือไม่มี ให้ใส่ null

            6. firstYearStudentProblems
            - จากหัวข้อ "ปัญหาของนักศึกษาแรกเข้า"

            7. studentLimitationStrategies
            - จากหัวข้อ "กลยุทธ์ในการดำเนินการเพื่อแก้ไขปัญหา/ข้อจำกัด"
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

admissionType2

admissionQualifications

admissionSelectionProcess

studentsPerYear

studentAdmissionPlans
  planName
  amount
  rows
    sequence
    rowType
    years

firstYearStudentProblems

studentLimitationStrategies
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {
                "type": ["string", "null"],
                "description": "UUID ของหลักสูตร (ถ้าไม่พบให้เป็น null)"
            },

            "admissionType2": {
                "type": ["string", "null"],
                "enum": [
                    "thai",
                    "international",
                    "thai-and-international"
                ]
            },

            "admissionQualifications": {
                "type": ["string", "null"]
            },

            "admissionSelectionProcess": {
                "type": ["string", "null"]
            },

            "studentsPerYear": {
                "type": ["integer", "null"]
            },

            "studentAdmissionPlans": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "planName": {
                            "type": ["string", "null"]
                        },
                        "amount": {
                            "type": ["integer", "null"]
                        },
                        "rows": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sequence": {
                                        "type": "integer"
                                    },
                                    "rowType": {
                                        "type": ["string", "null"]
                                    },
                                    "years": {
                                        "type": ["object", "null"],
                                        "additionalProperties": {
                                            "type": ["integer", "null"]
                                        }
                                    }
                                },
                                "required": ["sequence", "rowType", "years"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["planName", "rows"],
                    "additionalProperties": False
                }
            },

            "firstYearStudentProblems": {
                "type": ["string", "null"]
            },

            "studentLimitationStrategies": {
                "type": ["string", "null"]
            }
        },
        "required": [],
        "additionalProperties": False
    }


    return schema, prompt