def schema_prompt(chunk_pdf_bytes: bytes=None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 2

curriculumId Null

##การติ๊กมักมีรูปแบบที่เหมือนกัน และในแต่ละหัวข้อข้อที่ถูกติ๊กมักน้อยกว่าข้อที่ไม่ถูกติ๊ก

จากหัวข้อ การรับเข้าศึกษา
admissionType2 ให้เลือกค่าที่ติ้ก "thai" รับเฉพาะนักศึกษาไทย,"international" รับทั้งนักศึกษาไทยและนักศึกษาต่างชาติ ที่สามารถใช้ภาษาไทยได้ดี,"thai-and-international" รับทั้งนักศึกษาไทยและนักศึกษาต่างชาติ

จากหัวข้อ คุณสมบัติของผู้เข้าศึกษา
admissionQualifications คุณสมบัติของผู้เข้าศึกษา หากมีหลายข้อ ให้คั่นด้วย ","
admissionSelectionProcess การคัดเลือกผู้เข้าศึกษา

จากหัวข้อ แผนการรับนักศึกษาและผู้สำเร็จการศึกษาในระยะ 5 ปี
studentsPerYear จำนวน ในแต่ละปีการศึกษาจะรับนักศึกษาปีละ

studentAdmissionPlans เป็นตารางที่มี 2 column หลัก 'จํานวนนักศึกษา' และ 'จํานวนนักศึกษาแต่ละปีการศึกษา' โดย 'จํานวนนักศึกษาแต่ละปีการศึกษา' จะมี column ย่อยเป็น ปี ต่างๆ
head_studentAdmissionPlans คือ column ย่อยทั้งหมดของ column 'จํานวนนักศึกษาแต่ละปีการศึกษา'
  planName คำว่า 'แผนการรับนักศึกษา รุ่นปี ' + ปีที่น้อยที่สุดที่เจอใน column ย่อยของ 'จํานวนนักศึกษาแต่ละปีการศึกษา'
  amount มีค่าเป็น 0
  rows
    sequence null
    rowType เป็นค่าจาก column 'จํานวนนักศึกษา'
    years 
      BEyear ค่า column ย่อยทั้งของ 'จํานวนนักศึกษาแต่ละปีการศึกษา'
      detail_year จำนวนที่แต่ละปีนั้น (หากไม่มีให้เป็น 0)

จากหัวข้อ ปัญหาของนักศึกษาแรกเข้า
firstYearStudentProblems หากมีหลายข้อ ให้ คั่นด้วย ","

จากหัวข้อ กลยุทธ์ในการดําเนินการเพื่อแก้ไขปัญหา/ข้อจํากัดของนักศึกษาในข้อ 2.4
studentLimitationStrategies หากมีหลายข้อ ให้ คั่นด้วย ","
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
                        "head_studentAdmissionPlans": {
                            "type":"array",
                            "items":{
                                "type":"integer"
                                
                            },
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
                                    "type": ["array", "null"],
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                        "BEyear": {"type": ["integer", "null"]},
                                        "detail_year": {"type": ["integer", "null"]}
                                        },
                                        "required": ["BEyear", "detail_year"],
                                        "additionalProperties": False
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


    master_schema = {
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


    return schema, prompt, master_schema