def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 6

curriculumId null

curriculumNameG6 หลักสูตรและ สาขา เช่น (หลักสูตรวิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และนวัตกรรมข้อมูล)

physicalReadiness จากหัวข้อ ด้านกายภาพ
    classroom ห้องเรียน
    laboratory ห้องปฏิบัติการ
    learningFacilities สิ่งอํานวยความสะดวกเพื่อการเรียนรู้ (หากมีอธิบายย่อของต่างๆอีกทีเช่น เอกสาร มีจำนวนรวมทั้งหมด 12,809 เล่ม แบ่งเป็น ภาษาไทย ภาษาต่างประเทศ ให้เอามาแค่ ตัวเลขแบบรวม)
    otherPhysicalReadiness ความพร้อมด้านกายภาพอื่น ๆ

จากหัวข้อ ด้านวิชาการ
academicWorksSummaries จํานวนผลงานวิชาการ สิ่งประดิษฐ์ ผลงานอื่น ๆ ของอาจารย์ประจําหลักสูตร ในรอบ 5 ปีย้อนหลัง (เป็นตาราง ซึ่งมี 3 column หลัก 'จํานวนผลงานทางวิชาการ', 'จํานวนอาจารย์ประจําหลักสูตร (คน)' และ 'สัดส่วนอาจารย์ : ผลงาน' โดย 'จํานวนผลงานทางวิชาการ' มี 3 column ย่อย 'งานวิจัยหรือบทความวิจัย(ชิ้น)', 'ผลงานทางวิชาการอื่น ๆ เช่น ตํารา หนังสือ/บทความวิชาการอื่น ๆสิ่งประดิษฐ์ เป็นต้น(ชิ้น)' และ 'รวมผลงานทางวิชาการทั้งหมด (ชิ้น)' ใน 'สัดส่วนอาจารย์ : ผลงาน' มี 2 columns ย่อยคือ 'วิจัย' และ 'อื่น ๆ')
    researchCount จาก 'งานวิจัยหรือบทความวิจัย (ชิ้น)'
    academicWorkCount จาก 'ผลงานทางวิชาการอื่น ๆ เช่น ตํารา หนังสือ/บทความวิชาการอื่น ๆ สิ่งประดิษฐ์ เป็นต้น (ชิ้น)'
    totalAcademicWorks จาก 'รวมผลงานทางวิชาการทั้งหมด (ชิ้น)'
    fullTimeLecturerCount จาก 'จํานวนอาจารย์ประจําหลักสูตร (คน)'
    researchRatio จาก 'วิจัย' (เอามาแค่อัตรา)
    otherWorkRatio จาก 'อื่น ๆ' (เอามาแค่อัตรา)
    overallRatio รวม (เป็นช่องที่อยู่ด้านล่างของ 'วิจัย' 'อื่น ๆ' เอามาแค่อัตรา)
thesisAdvisors ความพร้อมของอาจารย์ที่ปรึกษาวิทยานิพนท์/ค้นคว้าอิสระ (เป็นตารางที่มี 3 column หลัก 'ลำดับ', 'อาจารย์ที่ปรึกษาหลักสูตร' และ 'จำนวนนักศึกษาที่รับเป็นที่ปรึกษาวิทยานิพนท์/ค้นคว้าอิสระ (คน)' โดย 'จำนวนนักศึกษาที่รับเป็นที่ปรึกษาวิทยานิพนท์/ค้นคว้าอิสระ (คน)' แบ่งเป็น 3 column ย่อย 'จำนวนที่รับได้ทั้งหมด', 'จำนวนรับในปัจจุบัน' และ 'จำนวนที่รับเพิ่มเติมได้')
    advisorName 'อาจารย์ที่ปรึกษาหลักสูตร'
    maxStudents 'จำนวนที่รับได้ทั้งหมด'
    currentStudents 'จำนวนรับในปัจจุบัน'
    availableSlots 'จำนวนที่รับเพิ่มเติมได้'

graduateProductionCost ค่าใช้จ่ายในการผลิตบัณฑิต ( เป็นตาราง ซึ่งมีcolumn 'ลำดับ' 'รายจ่าย' และ 'บาท/หลักสูตร' บางครั้งไม่มี 'ลำดับ' และ 'บาท/หลักสูตร' จะเป็นเลขปีแทน หากมีหลายปีให้เอาเลขปีที่น้อยที่สุด และเลขปีนั้นแทน 'บาท/หลักสูตร')
name 'รายจ่าย'
amount 'บาท/หลักสูตร'

educationIncome รายได้จากค่าธรรมเนียมการศึกษา/และอื่น ๆ ( เป็นตาราง ซึ่งมีcolumn 'ลำดับ' 'รายได้' และ 'บาท/หลักสูตร' บางครั้งไม่มี 'ลำดับ' และ 'บาท/หลักสูตร' จะเป็นเลขปีแทน หากมีหลายปีให้เอาเลขปีที่น้อยที่สุด และเลขปีนั้นแทน 'บาท/หลักสูตร')
name 'รายได้'
amount 'บาท/หลักสูตร'
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumNameG6": {"type": ["string", "null"]},

            "physicalReadiness": {
                "type": ["object", "null"],
                "properties": {
                    "classroom": {"type": ["string", "null"]},
                    "laboratory": {"type": ["string", "null"]},
                    "learningFacilities": {"type": ["string", "null"]},
                    "otherPhysicalReadiness": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "academicWorksSummaries": {
                "type": ["object", "null"],
                "properties": {
                    "researchCount": {"type": ["integer", "null"]},
                    "academicWorkCount": {"type": ["integer", "null"]},
                    "totalAcademicWorks": {"type": ["integer", "null"]},
                    "fullTimeLecturerCount": {"type": ["integer", "null"]},
                    "researchRatio": {"type": ["string", "null"]},
                    "otherWorkRatio": {"type": ["string", "null"]},
                    "overallRatio": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "thesisAdvisors": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "advisorName": {"type": ["string", "null"]},
                        "maxStudents": {"type": ["integer", "null"]},
                        "currentStudents": {"type": ["integer", "null"]},
                        "availableSlots": {"type": ["integer", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "graduateProductionCost": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "amount": {"type": ["number", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "educationIncome": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "amount": {"type": ["number", "null"]}
                    },
                    "additionalProperties": False
                },
            },
        "additionalProperties": False,
        "required" : ["curriculumNameG6","physicalReadiness","thesisAdvisors","graduateProductionCost","educationIncome"]
        },
    }

    master_schema = {
        "type": "object",
        "properties": {
            "curriculumNameG6": {"type": ["string", "null"]},

            "physicalReadiness": {
                "type": ["object", "null"],
                "properties": {
                    "classroom": {"type": ["string", "null"]},
                    "laboratory": {"type": ["string", "null"]},
                    "learningFacilities": {"type": ["string", "null"]},
                    "otherPhysicalReadiness": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "academicWorksSummaries": {
                "type": ["object", "null"],
                "properties": {
                    "researchCount": {"type": ["integer", "null"]},
                    "academicWorkCount": {"type": ["integer", "null"]},
                    "totalAcademicWorks": {"type": ["integer", "null"]},
                    "fullTimeLecturerCount": {"type": ["integer", "null"]},
                    "researchRatio": {"type": ["string", "null"]},
                    "otherWorkRatio": {"type": ["string", "null"]},
                    "overallRatio": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "thesisAdvisors": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "advisorName": {"type": ["string", "null"]},
                        "maxStudents": {"type": ["integer", "null"]},
                        "currentStudents": {"type": ["integer", "null"]},
                        "availableSlots": {"type": ["integer", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "graduateProductionCost": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "amount": {"type": ["number", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "educationIncome": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": ["string", "null"]},
                        "amount": {"type": ["number", "null"]}
                    },
                    "additionalProperties": False
                }
            },

            "breakEvenAnalysis": {
                "type": ["object", "null"],
                "properties": {
                    "revenuePerStudent": {"type": ["number", "null"]},
                    "costPerStudent": {"type": ["number", "null"]},
                    "breakEvenStudentCount": {"type": ["integer", "null"]}
                },
                "additionalProperties": False
            },

            "managementReadiness": {
                "type": ["object", "null"],
                "properties": {
                    "lecturerCount": {"type": ["integer", "null"]},
                    "staffCount": {"type": ["integer", "null"]},
                    "teachingSkillDevelopment": {"type": ["string", "null"]},
                    "professionalSkillDevelopment": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "courseLecturers": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "fullName": {"type": ["string", "null"]},
                        "position": {"type": ["string", "null"]},
                        "courseRole": {"type": ["string", "null"]},
                        "qualifications": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "degree": {"type": ["string", "null"]},
                                    "major": {"type": ["string", "null"]},
                                    "institute": {"type": ["string", "null"]},
                                    "graduationYearBe": {"type": ["integer", "null"]}
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            }
        },
        "additionalProperties": False
    }

    return schema, prompt, master_schema
