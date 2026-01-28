def schema_prompt(chunk_pdf_bytes: bytes = None):


    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 4

curriculumId

จากหัวข้อ ระบบการจัดการศึกษาและระยะเวลาการศึกษา
educationSystem ระบบ (เอามาทั้งหมดในหัวข้อย่อย ระบบ)
isMaxStudyDurationYears จาก ระยะเวลาการศึกษาสูงสุด (true หากมีกำหนด false หากไม่มีกำหนด)
maxStudyDurationYears จาก ระยะเวลาการศึกษาสูงสุด (ข้อความทั้งหมด หากมีการกำหนดระยะเวลา)

จากหัวข้อ การดําเนินการหลักสูตร
teachingSchedule วัน-เวลา ในการดําเนินการเรียนการสอน
  sequence null
  semesterName ภาคการศึกษา (ภาคการศึกษาที่ 1 ,ภาคการศึกษาที่ 2 รวมถึง ภาคฤดูร้อน)
  start เดือนที่เริ่มต้น (เอาแค่เดือน)
  end เดือนที่สิ้นสุด (เอาแค่เดือน)
curriculumStudySystem ระบบการศึกษา เลือกจากข้อที่ติ้ก "ONSITE" คือ แบบชั้นเรียน (Onsite),"ONLINE" แบบทางไกล (Online),"HYBRID"แบบผสม (Hybrid)
curriculumStudySystemOther ระบบการศึกษา หากมีการเลือก อื่นๆ หรือมีการเลือกหลายค่า(ให้เอาค่าที่ถูกเลือกมาทั้งหมดและคั่นด้วย ",")

จากหัวข้อ การเทียบโอนหน่วยกิต รายวิชาและการลงทะเบียนเรียนข้ามสถาบันอุดมศึกษา
transferCurriculumLevel เลือกโดย "BACHELOR" คือปริญญาตรี,"MASTER" คือปริญญาโท,"DOCTOR" คือปริญญาเอก
transferAcademicYear ปีของข้อบังคับนั้น จากหัวข้อ การเทียบโอนหน่วยกิต

curriculumTotalCredits จำนวนหน่วยกิตรวม

จากหัวข้อ โครงสร้างหลักสูตร
minimumCurriculumCredits จำนวนหน่วยกิต ที่ต้องจดทะเบียบขั้นต่ำ
curriculumStructures
  sequence null
  courseGroup หมวดวิชาใหญ่
  courseCredits จำนวนหน่วยกิตของ หมวดวิชาใหญ่
  subCourseGroups (จะลงรายละเอียดไปอีกแค่ หนึ่งขั้น ถ้ามีการลงรายละเอียดอีกจะไม่นับ)
    subCourseGroup หมวดวิชาย่อย
    credits จำนวนหน่วยกิตของ หมวดวิชาใหญ่
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
            "educationSystem": {"type": ["string", "null"]},
            "isMaxStudyDurationYears": {"type": ["boolean", "null"]},
            "maxStudyDurationYears": {"type": ["string", "null"]},
            "teachingSchedule": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "null"},
                        "semesterName": {"type": "string"},
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    },
                    "required": ["sequence", "semesterName","start","end"],
                },
            },
            "curriculumStudySystem": {
                "type": ["string", "null"],
                "enum": ["ONSITE" ,"ONLINE" ,"HYBRID"],
                },
            "curriculumStudySystemOther": {"type": ["string", "null"]},
            "transferCurriculumLevel": {
                "type": ["string", "null"],
                "enum": ["BACHELOR" ,"MASTER" ,"DOCTOR"],},
            "transferAcademicYear": {"type": ["string", "null"]},
            "curriculumTotalCredits": {"type": ["integer", "null"]},
            "minimumCurriculumCredits": {"type": ["integer", "null"]},
            "curriculumStructures": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "integer"},
                        "courseGroup": {"type": "string"},
                        "courseCredits": {"type": "integer"},
                        "subCourseGroups": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "subCourseGroup": {"type": "string"},
                                    "credits": {"type": "integer"},
                                },
                                "required": ["subCourseGroup", "credits"],
                            },
                        },
                    },
                    "required": ["sequence", "courseGroup"],
                },
            },
        },
        "additionalProperties": False,
        "required": ["teachingSchedule","curriculumStudySystem","curriculumStudySystemOther","curriculumTotalCredits","curriculumStructures"]
    }

    return schema, prompt
