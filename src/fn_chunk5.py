def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF (เรียงจากบนลงล่าง)
        ❗ ห้ามอธิบายเพิ่มเติม
        ❗ ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

        หมวดที่ 5

        1. การพัฒนาคุณลักษณะของนักศึกษา
        - generalCharacteristics: คุณลักษณะทั่วไป + PLO ที่เกี่ยวข้อง
        - professionalCharacteristics: คุณลักษณะด้านวิชาชีพ + PLO ที่เกี่ยวข้อง

        2. ความสอดคล้อง PLO กับมาตรฐาน (Bloom / Generic / Specific)
        - ระบุ PLO
        - ระบุ domain และ level ของ Bloom
        - ติ๊ก true / false ให้ครบ

        3. กลยุทธ์การสอนและการประเมินผลตาม PLO

        4. Curriculum Mapping
        - แยกตามกลุ่มวิชา
        - รายวิชา / หน่วยกิต / ชั้นปี
        - ระบุ PLO ที่เชื่อมโยงเป็น true/false

        5. ความคาดหวังผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา

        6. การฝึกประสบการณ์ภาคสนาม (ถ้ามี)

        7. โครงงาน / วิจัย / วิทยานิพนธ์ (ถ้ามี)
        """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},

            "studentCharacteristicDevelopment": {
                "type": ["object", "null"],
                "properties": {
                    "generalCharacteristics": {
                        "type": ["object", "null"],
                        "properties": {
                            "description": {"type": ["string", "null"]},
                            "relatedPlos": {"type": ["string", "null"]}
                        },
                        "additionalProperties": False
                    },
                    "professionalCharacteristics": {
                        "type": ["object", "null"],
                        "properties": {
                            "description": {"type": ["string", "null"]},
                            "relatedPlos": {"type": ["string", "null"]}
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            },

            "ploStandardAlignment": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "ploCode": {"type": ["string", "null"]},
                        "isGeneric": {"type": ["boolean", "null"]},
                        "isSpecific": {"type": ["boolean", "null"]},
                        "bloomDomain": {"type": ["string", "null"]},
                        "bloomLevel": {"type": ["string", "null"]},
                        "hasKnowledge": {"type": ["boolean", "null"]},
                        "hasSkill": {"type": ["boolean", "null"]},
                        "hasEthics": {"type": ["boolean", "null"]},
                        "hasCharacter": {"type": ["boolean", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "ploTeachingAssessment": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "ploCode": {"type": ["string", "null"]},
                        "teachingStrategy": {"type": ["string", "null"]},
                        "assessmentMethod": {"type": ["string", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "curriculumMapping": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "courseGroup": {"type": ["string", "null"]},
                        "courses": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "subCourseGroup": {"type": ["string", "null"]},
                                    "credits": {"type": ["integer", "null"]},
                                    "yearLevel": {"type": ["integer", "null"]},
                                    "plos": {
                                        "type": ["object", "null"],
                                        "additionalProperties": {"type": ["boolean", "null"]}
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            },

            "yearEndLearningOutcomeExpectations": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "yearLevel": {"type": ["integer", "null"]},
                        "expectations": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "expectation": {"type": ["string", "null"]},
                                    "plos": {
                                        "type": ["object", "null"],
                                        "additionalProperties": {"type": ["boolean", "null"]}
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            },

            "fieldExperience": {
                "type": ["object", "null"],
                "properties": {
                    "period": {"type": ["string", "null"]},
                    "preparation": {"type": ["string", "null"]},
                    "assessment": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "projectResearchRequirement": {
                "type": ["object", "null"],
                "properties": {
                    "period": {"type": ["string", "null"]},
                    "preparation": {"type": ["string", "null"]},
                    "assessment": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    return schema, prompt
