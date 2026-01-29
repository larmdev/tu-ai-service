def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด ไม่ต้องเอาหัวข้อมาเช่น 9.3 การประเมินผลการดําเนินงานตามรายละเอียดหลักสูตร ,9.4 การทบทวนผลการประเมินและวางแผนปรับปรุง/พัฒนาหลักสูตร แต่ยังคงเอาเนื้อหาทั้งหมด
ข้อมูลจากหมวดที่ 9

curriculumId เป็น Null

อยู่ใน การประเมินประสิทธิผลของการสอน
courseTeachingEffectiveness การประเมินประสิทธิผลของการสอนระดับรายวิชา (ข้อความที่อยู่ในข้อนี้เอาทั้งหมด)
teachingManagementEvaluation การประเมินการจัดการเรียนการสอนของอาจารย์ (ข้อความที่อยู่ในข้อนี้เอาทั้งหมด)
 
overallCurriculumEvaluation การประเมินหลักสูตรในภาพรวม/ผลการดําเนินงานของหลักสูตร/ผลการประกันคุณภาพการศึกษา (ข้อความที่อยู่ในข้อนี้เอาทั้งหมด)

curriculumImplementationEvaluation การประเมินผลการดําเนินงานตามรายละเอียดหลักสูตร (ข้อความที่อยู่ในข้อนี้เอาทั้งหมด)

curriculumReviewAndImprovement การทบทวนผลการประเมินและวางแผนปรับปรุง/พัฒนาหลักสูตร

มาจากตาราง แผนปรับปรุงและพัฒนาหลักสูตร โดยตารางจะมี 2 column มีหัวข้อเป็น 'การพัฒนาหลักสูตร' และ 'วิธีการดําเนินการ' คำว่า 'จุดเด่น' และ 'จุดด้อย' จะอยู่ในช่องข้อมูลของ 'การพัฒนาหลักสูตร' อยู่แล้ว
curriculumImprovementStrengths เป็นค่าของ ที่เป็น 'จุดเด่น' (มีสมาชิกแค่ 1 ตัว)
    sequence คือ 1
    name ข้อมูลทั้งหมดของ การพัฒนาหลักสูตร ใน จุดเด่น (หากมีหลายข้อให้คั่นด้วย ",")
    detail ข้อมูลทั้งหมดของ วิธีการดําเนินการ ใน จุดเด่น (หากมีหลายข้อให้คั่นด้วย ",")
curriculumImprovementWeaknesses เป็นค่าของ ที่เป็น 'จุดด้อย' หรือ 'จุดที่ยังต้องพัฒนา' (มีสมาชิกแค่ 1 ตัว)
    sequence คือ 1
    name ข้อมูลทั้งหมดของ การพัฒนาหลักสูตร ใน จุดด้อย (หากมีหลายข้อให้คั่นด้วย ",")
    detail ข้อมูลทั้งหมดของ วิธีการดําเนินการ ใน จุดด้อย (หากมีหลายข้อให้คั่นด้วย ",")
    """

    schema = {
        "type": "object",
        "properties": {

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

    master_schema = {
        "type": "object",
        "properties": {
            
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

    return schema, prompt, master_schema
