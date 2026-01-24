def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF (เรียงจากบนลงล่าง)
        ❗ ห้ามอธิบาย
        ❗ ตอบเป็น JSON อย่างเดียว ตาม schema

        หมวดที่ 6 (หรือหมวดความพร้อมและศักยภาพ)

        1. ชื่อหลักสูตร (ภาษาไทย)

        2. ความพร้อมด้านกายภาพ
        - ห้องเรียน
        - ห้องปฏิบัติการ
        - แหล่งเรียนรู้
        - อื่น ๆ (ถ้ามี)

        3. ผลงานทางวิชาการของอาจารย์
        - จำนวนงานวิจัย
        - ผลงานทางวิชาการ
        - อัตราส่วนงานต่ออาจารย์ประจำ

        4. อาจารย์ที่ปรึกษาวิทยานิพนธ์ / โครงงาน
        - จำนวนที่รับได้
        - จำนวนที่ดูแลอยู่
        - จำนวนที่ยังรับได้

        5. ต้นทุนการผลิตบัณฑิต
        - แยกตามรายการ
        - ระบุจำนวนเงิน

        6. รายได้จากการจัดการศึกษา

        7. วิเคราะห์จุดคุ้มทุน
        - รายได้ต่อคน
        - ต้นทุนต่อคน
        - จำนวนนักศึกษาที่คุ้มทุน

        8. ความพร้อมด้านการบริหารจัดการ
        - จำนวนอาจารย์
        - จำนวนเจ้าหน้าที่
        - การพัฒนาทักษะการสอน
        - การพัฒนาวิชาชีพ

        9. อาจารย์ผู้สอน
        - ชื่อ
        - ตำแหน่ง
        - บทบาท
        - คุณวุฒิ (หลายรายการได้)
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

curriculumNameG6

physicalReadiness
classroom
laboratory
learningFacilities
otherPhysicalReadiness

academicWorksSummaries
researchCount
academicWorkCount
totalAcademicWorks
fullTimeLecturerCount
researchRatio
otherWorkRatio
overallRatio

thesisAdvisors
advisorName
maxStudents
currentStudents
availableSlots

graduateProductionCost
name
amount

educationIncome
name
amount

breakEvenAnalysis
revenuePerStudent
costPerStudent
breakEvenStudentCount

managementReadiness
lecturerCount
staffCount
teachingSkillDevelopment
professionalSkillDevelopment

courseLecturers
  fullName
  position
  courseRole
  qualifications
    degree
    major
    institute
    graduationYearBe
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
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

    return schema, prompt
