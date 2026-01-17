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

        ตัวอย่างข้อมูล
        {
            "curriculumId": "c3da8b60-9537-4f85-8b9b-0cc9031af789",

            "educationSystem": "ระบบทวิภาค โดย 1 ปีแบ่งออกเป็น 2 ภาคการศึกษา",

            "isMaxStudyDurationYears": true,
            "maxStudyDurationYears": "ไม่เกิน 8 ปีการศึกษา",

            "isRegularClassTime": true,
            "teachingSchedule": [
                {
                "sequence": 1,
                "semesterName": "ภาคเรียนที่ 1",
                "start": "สิงหาคม",
                "end": "ธันวาคม"
                },
                {
                "sequence": 2,
                "semesterName": "ภาคเรียนที่ 2",
                "start": "มกราคม",
                "end": "พฤษภาคม"
                }
            ],

            "curriculumStudySystem": "ONSITE",
            "curriculumStudySystemOther": null,

            "transferCurriculumLevel": "BACHELOR",
            "transferAcademicYear": "2566",

            "curriculumTotalCredits": 135,
            "minimumCurriculumCredits": 120,

            "curriculumStructures": [
                {
                "sequence": 1,
                "courseGroup": "วิชาศึกษาทั่วไป",
                "courseCredits": 30,
                "subCourseGroups": [
                    {
                    "subCourseGroup": "วิชาบังคับ",
                    "credits": 24
                    },
                    {
                    "subCourseGroup": "วิชาเลือก",
                    "credits": 6
                    }
                ]
                }
            ],

            "courses": [
                        {
                            "sequence": 1,
                            "courseCodeTh": "ว.ทบ.102",
                            "courseCodeEn": "CS102",
                            "courseNameTh": "การเขียนโปรแกรมคอมพิวเตอร์เบื้องต้น",
                            "courseNameEn": "Introduction to Computer Programming",
                            "courseDescriptionTh": "รายวิชานี้มุ่งเน้นให้นักศึกษาเข้าใจหลักการเขียนโปรแกรมเบื้องต้น",
                            "courseDescriptionEn": "This course introduces fundamental concepts of computer programming.",
                            "credits": 3,
                            "lecturePracticeSelfStudy": "2-2-5",
                            "courseGroup": "วิชาศึกษาทั่วไป",
                            "semester": 1,
                            "academicYear": 2569
                        },
                        {
                            "sequence": 2,
                            "courseCodeTh": "วทบ.101",
                            "courseCodeEn": "CS101",
                            "courseNameTh": "การเขียนโปรแกรมเบื้องต้น ag1",
                            "courseNameEn": "Introduction to Programming",
                            "courseDescriptionTh": "พื้นฐานการเขียนโปรแกรม",
                            "courseDescriptionEn": "Basic programming concepts",
                            "credits": 3,
                            "lecturePracticeSelfStudy": "3-1-5",
                            "courseGroup": "วิชาศึกษาทั่วไป",
                            "semester": 1,
                            "academicYear": 2567
                        }
            ],

            "academicRequirements": [
                {
                "sequence": 1,
                "title": "โครงงาน",
                "detail": "นักศึกษาต้องจัดทำโครงงานก่อนสำเร็จการศึกษา"
                }
            ]
        }

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
                        "sequence": {"type": "integer"},
                        "semesterName": {"type": "string"},
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    },
                    "required": ["sequence", "semesterName"],
                },
            },
            "curriculumStudySystem": {"type": ["string", "null"]},
            "curriculumStudySystemOther": {"type": ["string", "null"]},
            "transferCurriculumLevel": {"type": ["string", "null"]},
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
                        "sequence": {"type": "integer"},
                        "courseCodeTh": {"type": ["string", "null"]},
                        "courseCodeEn": {"type": ["string", "null"]},
                        "courseNameTh": {"type": ["string", "null"]},
                        "courseNameEn": {"type": ["string", "null"]},
                        "courseDescriptionTh": {"type": ["string", "null"]},
                        "courseDescriptionEn": {"type": ["string", "null"]},
                        "credits": {"type": ["integer", "null"]},
                        "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                        "courseGroup": {"type": ["string", "null"]},
                        "semester": {"type": ["integer", "null"]},
                        "academicYear": {"type": ["integer", "null"]},
                    },
                    "required": ["sequence"],
                },
            },
            "academicRequirements": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "sequence": {"type": "integer"},
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
