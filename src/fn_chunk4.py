def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 

curriculumId

educationSystem

isMaxStudyDurationYears

maxStudyDurationYears

teachingSchedule
  sequence
  semesterName
  start
  end

curriculumStudySystem

curriculumStudySystemOther

transferCurriculumLevel

transferAcademicYear

curriculumTotalCredits

minimumCurriculumCredits

curriculumStructures
  sequence
  courseGroup
  courseCredits
  subCourseGroups
    subCourseGroup
    credits

courses
  sequence
  courseCodeTh
  courseCodeEn
  courseNameTh
  courseNameEn
  courseDescriptionTh
  courseDescriptionEn
  credits
  lecturePracticeSelfStudy
  courseGroup
  semester
  academicYear

academicRequirements
  sequence
  title
  detail
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
