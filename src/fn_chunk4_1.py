def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากไฟล์ที่ทำการ extract เรียงจากบนลงล่าง
        ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

        หมวดที่ 4 ระบบการจัดการศึกษาและโครงสร้างหลักสูตร

        - educationSystem จากหัวข้อ ระบบการจัดการศึกษา
        - isMaxStudyDurationYears ให้เป็น true ถ้ามีข้อความกำหนดระยะเวลาศึกษาสูงสุด
        - maxStudyDurationYears เอาข้อความเต็ม เช่น "ไม่เกิน 8 ปีการศึกษา"

        - teachingSchedule จากตารางภาคการศึกษา
            - sequence เรียงตามลำดับ
            - semesterName
            - start เดือนเริ่ม
            - end เดือนสิ้นสุด

        - curriculumStudySystem เช่น ONSITE / ONLINE / HYBRID
        - curriculumStudySystemOther ถ้ามีคำอื่นนอกเหนือจากตัวเลือก

        - transferCurriculumLevel ระดับหลักสูตรที่รับโอน
        - transferAcademicYear ปีการศึกษาที่เริ่มใช้

        - curriculumTotalCredits หน่วยกิตรวมทั้งหลักสูตร
        - minimumCurriculumCredits หน่วยกิตขั้นต่ำ

        (ต่อไปเป็นโครงสร้างหลักสูตร)
        - curriculumStructures
            - courseGroup
            - courseCredits
            - subCourseGroups

        (ต่อไปเป็นตารางรายวิชา)
        - courses ทุกแถวของตารางรายวิชา

        (ต่อไปเป็นข้อกำหนดทางวิชาการ)
        - academicRequirements เอาทั้งหมดเรียงลำดับ

        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 4

curriculumId

จากหัวข้อ ระบบการจัดการศึกษาและระยะเวลาการศึกษา
educationSystem ระบบ
isMaxStudyDurationYears จาก ระยะเวลาการศึกษาสูงสุด (true หากมีกำหนด false หากไม่มีกำหนด)
maxStudyDurationYears จาก ระยะเวลาการศึกษาสูงสุด (ข้อความทั้งหมด หากมีการกำหนดระยะเวลา)

จากหัวข้อ การดําเนินการหลักสูตร
teachingSchedule วัน-เวลา ในการดําเนินการเรียนการสอน
  sequence null
  semesterName ภาคการศึกษา (รวมถึง ภาคฤดูร้อน)
  start เดือน ที่เริ่มต้น
  end เดือน ที่สิ้นสุด
curriculumStudySystem ระบบการศึกษา เลือกจากข้อที่ติ้ก "ONSITE" คือ แบบชั้นเรียน (Onsite),"ONLINE" แบบทางไกล (Online),"HYBRID"แบบผสม (Hybrid)
curriculumStudySystemOther ระบบการศึกษา หากมีการเลือก อื่นๆ หรือมีการเลือกหลายค่า(ให้เอาค่าที่ถูกเลือกมาทั้งหมดและคั่นด้วย ",")

จากหัวข้อ การเทียบโอนหน่วยกิต รายวิชาและการลงทะเบียนเรียนข้ามสถาบันอุดมศึกษา
transferCurriculumLevel เลือกโดย "BACHELOR" คือปริญญาตรี,"MASTER" คือปริญญาโท,"DOCTOR" คือปริญญาเอก
transferAcademicYear ปีของข้อบังคับนั้น

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

courses
จากหัวข้อ รายวิชาและข้อกําหนดของหลักสูตร
  sequence null
  courseGroup หมวดรายวิชาใหญ่ (ต้องเป็นค่าที่อยู่ใน ourseGroup จาก curriculumStructures เท่านั้น)
  lecturePracticeSelfStudy
  courseCodeTh รหัสวิชา ภาษาไทย
  courseCodeEn รหัสวิชา ภาษาอังกฤษ
  courseNameTh ชื่อรายวิชา ภาษาไทย
  courseNameEn ชื่อรายวิชา ภาษาอังกฤษ
  credits หน่วยกิต (เป็นเลขเดี่ยวๆอยู่ด้านหลัง ชื่อวิชาภาษาไทย)

จากหัวข้อ แผนการศึกษา
structure (เป็นตารางที่ส่วนมาก จะมี 1 column เป็นปีการศึกษา และจะมีแยกอีก 2 columns เป็นภาคการศึกษากับ หน่วยกิต ไม่เอาหน่วยกิตรวม ส่วนมาก ชื่อวิชาจะอยู่ในช่องเดียวกันหมด)
    academicYear ปีการศึกษา
    semester ภาคการศึกษา
    courseTh รหัส และชื่อวิชาภาษาไทย
    credits หน่วยกิต (เป็นเลขเดี่ยวๆ)
    lecturePracticeSelfStudy รายละเอียดหน่วยกิต (เป็นข้อความจากในวงเล็บด้านหลังหน่วยกิต ส่วนมากจะเป็น format เช่น 2-2-5 หรือ มากกว่า 500 ชั่วโมง)

academicRequirements จากหัวข้อ ข้อกำหนดการทำวิทยานิพนธ์ การค้นคว้าอิสระ การสอบประมวลความรู้ และการสอบวัตคุณสมบัติ
  sequence null
  title หัวข้อ
  detail รายละเอียด
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
                    "required": ["sequence", "semesterName"],
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
            "courses": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "null"},
                        "courseCodeTh": {"type": ["string", "null"]},
                        "courseCodeEn": {"type": ["string", "null"]},
                        "courseNameTh": {"type": ["string", "null"]},
                        "courseNameEn": {"type": ["string", "null"]},
                        "credits": {"type": ["integer", "null"]},
                        "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                        "courseGroup": {"type": ["string", "null"]},
                        "semester": {"type": ["integer", "null"]},
                        "academicYear": {"type": ["integer", "null"]},
                    },
                    "required": ["sequence"],
                },
            },
            "structure": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "academicYear": {"type": ["integer", "null"]},
                        "semester": {"type": ["integer", "null"]},
                        "courseTh": {"type": ["string", "null"]},
                        "credits": {"type": ["integer", "null"]},
                        "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                    },
                    "required": ["sequence"],
                },
            },
            "academicRequirements": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "null"},
                        "title": {"type": "string"},
                        "detail": {"type": ["string", "null"]},
                    },
                    "required": ["sequence", "title"],
                },
            },
        },
        "additionalProperties": False,
    }

    return schema, prompt
