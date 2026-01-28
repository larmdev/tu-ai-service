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

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 5

curriculumId เป็น null

จากหัวข้อ การพัฒนาคุณลักษณะของนักศึกษาในหลักสูตร
studentCharacteristicDevelopment (เป็นตารางที่มี 2 column 'คุณลักษณะของนักศึกษา' และ 'ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs)' โดยใน 'คุณลักษณะของนักศึกษา' จะคำว่า คุณลักษณะบุคคลทั่วไป และ คุณลักษณะบุคคลตามวิชาชีพหรือศาสตร์ อยู่ในนั้น และบางที 'คุณลักษณะของนักศึกษา' ก็จะมีทุกข้อรวมในช่องเดียว บางทีก็จะเป็นข้อละแถว)
  generalCharacteristics ('คุณลักษณะของนักศึกษา' ที่อยู่ใน คุณลักษณะบุคคลทั่วไป)
    description คุณลักษณะของนักศึกษา (รวมมาทั้งหมด)
    relatedPlos ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) (รวมมาทั้งหมด)
  professionalCharacteristics ('คุณลักษณะของนักศึกษา' ที่อยู่ใน คุณลักษณะบุคคลตามวิชาชีพหรือศาสตร์)
    description คุณลักษณะของนักศึกษา (รวมมาทั้งหมด)
    relatedPlos ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) (รวมมาทั้งหมด)

จากหัวข้อ ตารางแสดงความสัมพันธ์ระหว่างผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) กับมาตรฐานคุณวุฒิระดับอุดมศึกษา พ.ศ. 2565
ploStandardAlignment (เป็นตารางที่มี 4 column 'ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs)' ,'ประเภท' ,'Blooms Taxonomy' และ 'รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา พ.ศ. 2565' โดย 'ประเภท' มี 2 column ย่อย 'ทั่วไป(Generic)' และ 'เฉพาะ (Specific)' , 'Bloom’s Taxonomy' มี 2 column ย่อย  'Domain' และ 'Level' สุดท้าย 'รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา พ.ศ. 2565' มีหลาย column ย่อย ส่วนมากจะเป็น 'ความรู้ (Knowledge)' ,'ทักษะ (Skill)' ,'จริยธรรม (Ethic)' และ 'ลักษณะบุคคล (Character)' บางทีอาจมีตัวอื่นเช่น 'จริยธรรมลักษณะบุคคล (Attitude)')
  ploCode 'ผลลัพธ์การเรียนรู้ของหลักสูตร(PLOs)'
  isGeneric 'ทั่วไป(Generic)' (หากมีค่าให้เป็น true หากไม่มี flase)
  isSpecific 'เฉพาะ (Specific)' (หากมีค่าให้เป็น true หากไม่มี flase)
  bloomDomain 'Domain'
  bloomLevel 'Level'
  hasKnowledge 'ความรู้ (Knowledge)' (หากมีค่าให้เป็น true หากไม่มี flase)
  hasSkill 'ทักษะ (Skill)' (หากมีค่าให้เป็น true หากไม่มี flase)
  hasEthics 'จริยธรรม (Ethic)' (หากมีค่าให้เป็น true หากไม่มี flase)
  hasCharacter 'ลักษณะบุคคล (Character)' (หากมีค่าให้เป็น true หากไม่มี flase)

จากหัวข้อ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) กลยุทธ์/วิธีการสอน และ กลยุทธ์/วิธีการวัดและการประเมินผล
ploTeachingAssessment (เป็นตารางที่มี 3 column 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร' ,'กลยุทธ์/วิธีการสอน' และ 'วิธีการวัดและประเมินผล')
  ploCode 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร'
  teachingStrategy 'กลยุทธ์/วิธีการสอน'
  assessmentMethod 'วิธีการวัดและประเมินผล'
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
                        "additionalProperties": False,
                        "required":["description","relatedPlos"]
                    },
                    "professionalCharacteristics": {
                        "type": ["object", "null"],
                        "properties": {
                            "description": {"type": ["string", "null"]},
                            "relatedPlos": {"type": ["string", "null"]}
                        },
                        "additionalProperties": False,
                        "required":["description","relatedPlos"]
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

        },
        "additionalProperties": False,
        "required":["studentCharacteristicDevelopment","ploStandardAlignment","ploTeachingAssessment"]
    }

    master_schema = {
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


    return schema, prompt, master_schema
