def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 4

curriculumId

courses
จากหัวข้อ รายวิชาและข้อกําหนดของหลักสูตร
  sequence null
  courseGroup หมวดรายวิชาใหญ่ (ต้องเป็นค่า "วิชาศึกษาทั่วไป"หรือ "วิชาเฉพาะ" หรือ "วิชาเลือกเสรี" เท่านั้น)
    courseCodeTh รหัสวิชา ภาษาไทย
    courseNameTh ชื่อรายวิชา ภาษาไทย
    credits หน่วยกิต (มักมี format เป็น 3(3-0-6) หรือ 3(มากกว่า 570) ชั่วโมง เอามาแค่ตัวเลขหน้าวงเว็บ)
    lecturePracticeSelfStudy รายละเอียดหน่วยกิต (หน่วยกิต (มักมี format เป็น 3(3-0-6) หรือ 3(มากกว่า 570) ชั่วโมง เอามาแค่ในวงเว็บ))
    courseCodeEn รหัสวิชา ภาษาอังกฤษ (มักอยู่บรรทัดลงจากชื่อและรหัสภาษาไทย)
    courseNameEn ชื่อรายวิชา ภาษาอังกฤษ (มาหลังรหัสวิชาภาษาอังกฤษ)

จากหัวข้อ แผนการศึกษา
structure (เป็นตารางที่ส่วนมาก จะมี 1 column เป็นปีการศึกษา และจะมีแยกอีก 2 columns เป็นภาคการศึกษากับ หน่วยกิต ไม่เอาหน่วยกิตรวม ส่วนมาก ชื่อวิชาจะอยู่ในช่องเดียวกันหมด)
    academicYear ปีการศึกษา
    semester ภาคการศึกษา (1 หากเป็นภาคที่ 1, 2 หากเปนภาคที่ 2, 3 หากเป็นภาคฤดูร้อน)
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

            "courses": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "courseGroup": {"type": ["string", "null"]},
                        "detail_course": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sequence": {"type": "null"},
                                    "courseCodeTh": {"type": ["string", "null"]},
                                    "courseNameTh": {"type": ["string", "null"]},
                                    "credits": {"type": ["integer", "null"]},
                                    "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                                    "courseCodeEn": {"type": ["string", "null"]},
                                    "courseNameEn": {"type": ["string", "null"]},
                                },
                                "required": ["courseCodeTh","courseNameTh","credits","lecturePracticeSelfStudy","courseCodeEn","courseNameEn"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["courseGroup", "detail_course"],
                    "additionalProperties": False,
                },
            },

            "structure": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "academicYear": {"type": ["integer", "null"]},
                        "semester": {"type": ["integer", "null"]},
                        "detail": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "courseTh": {"type": ["string", "null"]},
                                    "credits": {"type": ["integer", "null"]},
                                    "lecturePracticeSelfStudy": {"type": ["string", "null"]},
                                },
                                "required": ["courseTh", "credits", "lecturePracticeSelfStudy"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["academicYear", "semester", "detail"],
                    "additionalProperties": False,
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
                    "additionalProperties": False,
                },
            },
        },
        "required": ["curriculumId", "structure", "academicRequirements"],
        "additionalProperties": False,
    }



#     prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
# ข้อมูลจากหมวดที่ 4

# curriculumId

# courses
# จากหัวข้อ รายวิชาและข้อกําหนดของหลักสูตร
#   sequence null
#   courseGroup หมวดรายวิชาใหญ่ (ต้องเป็นค่า "วิชาศึกษาทั่วไป"หรือ "วิชาเฉพาะ" หรือ "วิชาเลือกเสรี" เท่านั้น )
#     courseCodeTh รหัสวิชา ภาษาไทย
#     courseNameTh ชื่อรายวิชา ภาษาไทย
#     credits หน่วยกิต (มักมี format เป็น 3(3-0-6) หรือ 3(มากกว่า 570) ชั่วโมง เอามาแค่ตัวเลขหน้าวงเว็บ)
#     lecturePracticeSelfStudy รายละเอียดหน่วยกิต (หน่วยกิต (มักมี format เป็น 3(3-0-6) หรือ 3(มากกว่า 570) ชั่วโมง เอามาแค่ในวงเว็บ))
#     courseCodeEn รหัสวิชา ภาษาอังกฤษ
#     courseNameEn ชื่อรายวิชา ภาษาอังกฤษ (มาหลังรหัสวิชาภาษาอังกฤษ)
#     """

#     schema = {
#         "type": "object",
#         "properties": {
#             "curriculumId": {"type": ["string", "null"]},

            # "courses": {
            #     "type": ["array", "null"],
            #     "items": {
            #         "type": "object",
            #         "properties": {
            #             "courseGroup": {"type": ["string", "null"]},
            #             "detail_course": {
            #                 "type": ["array", "null"],
            #                 "items": {
            #                     "type": "object",
            #                     "properties": {
            #                         "sequence": {"type": "null"},
            #                         "courseCodeTh": {"type": ["string", "null"]},
            #                         "courseNameTh": {"type": ["string", "null"]},
            #                         "credits": {"type": ["integer", "null"]},
            #                         "lecturePracticeSelfStudy": {"type": ["string", "null"]},
            #                         "courseCodeEn": {"type": ["string", "null"]},
            #                         "courseNameEn": {"type": ["string", "null"]},
            #                     },
            #                     "required": ["sequence"],
            #                     "additionalProperties": False,
            #                 },
            #             },
            #         },
            #         "required": ["courseGroup", "detail_course"],
            #         "additionalProperties": False,
            #     },
#             },
#         },
#             "required": ["courses"],
#             "additionalProperties": False,
#         }


    return schema, prompt
