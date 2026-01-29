def schema_prompt(chunk_pdf_bytes: bytes | None = None):

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 1

curriculumId Null

approvalStatus ให้เป็น "in-progress" เท่านั้น
institutionName ให้ค่าเป็น "มหาวิทยาลัยธรรมศาสตร์"

facultyName คณะ/วิทยาลัย/สถาบัน (หากมี ศูนย์อยู่ด้านหลัง ไม่ต้องเอารายละเอียดศูนย์)
facultyCode Null

approvalDate
startDate

อยู่ในหัวข้อ รหัสและชื่อหลักสูตร
curriculumCodeTh รหัสหลักสูตร
curriculumCodeEn Null
curriculumNameTh ชื่อหลักสูตรภาษาไทย
curriculumNameEn ชื่อหลักสูตรภาษาอังกฤษ

อยู่ในหัวข้อ ชื่อปริญญาและสาขาวิชา
degreeFullTh ภาษาไทย ชื่อเต็ม
degreeAbbrTh ภาษาไทย ชื่อย่อ
degreeFullEn ภาษาอังกฤษ ชื่อเต็ม
degreeAbbrEn ภาษาอังกฤษ ชื่อย่อ

อยู่ในหัวข้อ วิชาเอก
majorsData (หากไม่มีให้เป็น Null)
  majorTh ภาษาไทย
  majorEn ภาษาอังกฤษ

##การติ๊กมักมีรูปแบบที่เหมือนกัน และในแต่ละหัวข้อข้อที่ถูกติ๊กมักน้อยกว่าข้อที่ไม่ถูกติ๊ก

อยู่ในหัวข้อ รูปแบบของหลักสูตร
curriculumLevel ให้เลือกค่าที่ติ้ก "bachelor" ปริญญาตรี, "master" ปริญญาโท, "doctor" ปริญญาเอก
curriculumFormat ให้เลือกค่าที่ติ้ก "continuing" ต่อเนื่อง, "1-years" 1 ปี,"2-years" 2 ปี,"3-years" 3 ปี,"4-years" 4 ปี,"5-years" 5 ปี,"6-years" 6 ปี

อยู่ในหัวข้อ ประเภทของหลักสูตร
curriculumType ให้เลือกค่าที่ติ้ก "academic" หลักสูตรปริญญาตรีทางวิชาการ,"progressive-academic" หลักสูตรปริญญาตรีแบบก้าวหน้าทางวิชาการ,"professional" หลักสูตรปริญญาตรีทางวิชาชีพหรือปฏิบัติการ,"progressive-professional" หลักสูตรปริญญาตรีแบบก้าวหน้าทางวิชาชีพหรือปฏิบัติการ
curriculumCategory Null

plan1
  isPlan ค่าเป็น false
  isThesisOnly ค่าเป็น false
  isCourseworkAndThesis ค่าเป็น false
  isPlan11 ค่าเป็น false
  isPlan12 ค่าเป็น false
  isPlan21 ค่าเป็น false
  isPlan22 ค่าเป็น false

plan2
  isPlan ค่าเป็น false
  isThesisOnly ค่าเป็น false
  isCourseworkAndThesis ค่าเป็น false
  isPlan11 ค่าเป็น false
  isPlan12 ค่าเป็น false
  isPlan21 ค่าเป็น false
  isPlan22 ค่าเป็น false

อยู่ในหัวข้อ ภาษาที่ใช้
instructionLanguage ให้เลือกค่าที่ติ้ก "thai" จัดการศึกษาเป็นภาษาไทย, "english" จัดการศึกษาเป็นภาษาอังกฤษ, "both" จัดการศึกษาทั้งภาษาไทยและภาษาอังกฤษ, "other" จัดการศึกษาเป็นภาษาต่างประเทศ
instructionLanguageOther รายละเอียดภาษาหากมีการติ้ก จัดการศึกษาเป็นภาษาต่างประเทศ

admissionType null

อยู่ในหัวข้อ ความร่วมมือกับสถาบันอื่น
isJointProgram เลือกค่าจากที่ติ้ก false เป็นหลักสูตรของสถาบันโดยเฉพาะ ,true เป็นหลักสูตรที่ได้รับความร่วมมือสนับสนุนจากสถาบันอื่น
jointInstitutionName รายละเอียด หากมีการติ้ก ความร่วมมือสนับสนุนจากสถาบันอื่น หากไม่มีให้เป็น Null

อยู่ในหัวข้อ การให้ปริญญาแก่ผู้สําเร็จการศึกษา
degreeConferralType เลือกค่าจากที่ติ้ก "single" ให้ปริญญาเพียงสาขาวิชาเดียว, "multiple" ให้ปริญญามากกว่า 1 สาขาวิชา

อยูในหัวข้อ สถานภาพของหลักสูตรและการพิจารณาอนุมัติ/เห็นชอบหลักสูตร
curriculumYear ปีของ หลักสูตรใหม่
openSemester ภาคการศึกษาที่ กําหนดเปิดสอน
openAcademicYear ปีที่ กําหนดเปิดสอน
approvedByPolicyCommitteeMeetingNumber ครั้งที่การประชุม (format ครั้ง/ปี เช่น 1/2567) ของ ได้พิจารณากลั่นกรองโดยคณะกรรมการนโยบายวิชาการ
approvedByPolicyCommitteeDate วันที่ ของ ได้พิจารณากลั่นกรองโดยคณะกรรมการนโยบายวิชาการ
approvedByUniversityCouncilMeetingNumber ครั้งที่การประชุม (format ครั้ง/ปี เช่น 1/2567) ของ ได้รับอนุมัติ/เห็นชอบหลักสูตรจากสภามหาวิทยาลัย
approvedByUniversityCouncilDate วันที่ ของ ได้รับอนุมัติ/เห็นชอบหลักสูตรจากสภามหาวิทยาลัย
approvedByProfessionalCouncilMeetingNumber ครั้งที่การประชุม (format ครั้ง/ปี เช่น 1/2567) ของ ได้รับอนุมัติ/เห็นชอบหลักสูตรจากสภาวิชาชีพ
approvedByProfessionalCouncilDate วันที่ ของ ได้รับอนุมัติ/เห็นชอบหลักสูตรจากสภาวิชาชีพ

อยู่ในหัวข้อ อาชีพที่สามารถประกอบได้หลังสำเร็จการศึกษา
careerPaths แต่ละข้อของ อาชีพ (เอามาแค่อาชีพ)

อยู่ในหัวข้อ สถานที่จัดการเรียนการสอน
instructionLocations เลือกจากค่าที่ถูกติ้ก "tha-phra-chan" ท่าพระจันทร์, "pattaya" ศูนย์รังสิต, "rangsit" ศูนย์พัทยา, "lampang" ศูนย์ลำปาง

อยู่ในหัวข้อ ค่าใช้จ่ายตลอดหลักสูตร
projectType ประเภทโครงการ เลือกจากค่าที่ติ้ก "normal" โครงการปกติ, "special" โครงการพิเศษ, "both" ทั้งโครงการปกติและ โครงการพิเศษ
isCostThaiStudent true หากมีการอธิบายค่าใช้จ่ายของ นักศึกษาไทย false หากไม่มี
costThaiStudent รายละเอียดค่าใช้จ่ายของ นักศึกษาไทย
isCostInternationalStudent  true หากมีการอธิบายค่าใช้จ่ายของ นักศึกษาต่างชาติ false หากไม่มี
costInternationalStudent รายละเอียดค่าใช้จ่ายของ นักศึกษาต่างชาติ

อยู่ในหัวข้อ การจัดการหลักสูตรตอบสนองต่อความต้องการของภาคส่วนต่าง ๆ
อยู่ในหัวข้อย่อย สถานการณ์ภายนอกหรือการพัฒนาที่จำเป็นต้องนำมาพิจารณาในการวางแผนพัฒนาหลักสูตร เพื่อจัดการความเสี่ยงและลดผลกระทบจากภายนอก
nationalPolicyStrategy2561_2580 การตอบสนองต่อนโยบายและยุทธศาสตร์ชาติ(พ.ศ. 2561-2580)
industry4_0Strategy2560_2579 การตอบสนองต่อยุทธศาสตร์การพัฒนาอุตสาหกรรมไทย 4.0 ระยะ 20 ปี
sdgAlignment การตอบสนองต่อเป้าหมายการพัฒนาที่ยั่งยืนขององค์การสหประชาชาติ SDG
institutionalAlignment อยู่ในหัวข้อย่อย ความสอดคล้องกับวิสัยทัศน์ยุทธศาสตร์ และพันธกิจของสถาบัน
stakeholderExpectations อยู่ในหัวข้อย่อย ความต้องการและความคาดหวังของผู้มีส่วนได้ส่วนเสีย

อยู่ในหัวข้อ มาตรฐานสากลของกลุ่มสาขาวิชากางการศึกษา (International Standard Classification of Education, ISCED) เป็นตารางที่มี 3 column broadField narrowField detailField
broadField
narrowField
detailField
remark เหตุผลในการเลือกให้หลักสูตรอยู่ภายใต้สาขาวิชานี้
    """

    plan_object_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "isPlan": {"type": "boolean"},
            "isThesisOnly": {"type": "boolean"},
            "isCourseworkAndThesis": {"type": "boolean"},
            "isPlan11": {"type": "boolean"},
            "isPlan12": {"type": "boolean"},
            "isPlan21": {"type": "boolean"},
            "isPlan22": {"type": "boolean"},
        },
        "required": [
            "isPlan",
            "isThesisOnly",
            "isCourseworkAndThesis",
            "isPlan11",
            "isPlan12",
            "isPlan21",
            "isPlan22",
        ],
    }

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
            "approvalStatus": {
                "type": "string",
                "enum": ["approved", "in-progress", "rejected", "cancelled", "other"],
            },
            "institutionName": {"type": ["string", "null"]},
            "facultyName": {"type": ["string", "null"]},
            "facultyCode": {"type": ["string", "null"]},
            "approvalDate": {"type": ["string", "null"], "format": "date-time"},
            "startDate": {"type": ["string", "null"], "format": "date-time"},

            "curriculumCodeTh": {"type": ["string", "null"]},
            "curriculumNameTh": {"type": ["string", "null"]},
            "curriculumCodeEn": {"type": ["string", "null"]},
            "curriculumNameEn": {"type": ["string", "null"]},

            "degreeFullTh": {"type": ["string", "null"]},
            "degreeAbbrTh": {"type": ["string", "null"]},
            "degreeFullEn": {"type": ["string", "null"]},
            "degreeAbbrEn": {"type": ["string", "null"]},

            "majorsData": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "majorTh": {"type": ["string", "null"]},
                        "majorEn": {"type": ["string", "null"]},
                    },
                },
            },

            "curriculumLevel": {
                "type": "string",
                "enum": ["bachelor", "master", "doctor"],
            },
            "curriculumFormat": {
                "type": "string",
                "enum": [
                    "continuing",
                    "1-years",
                    "2-years",
                    "3-years",
                    "4-years",
                    "5-years",
                    "6-years",
                ],
            },

            "curriculumType": {
                "type": ["string", "null"],
                "enum": [
                    "academic",
                    "progressive-academic",
                    "professional",
                    "progressive-professional",
                    None,
                ],
            },
            "curriculumCategory": {
                "type": ["string", "null"],
                "enum": [
                    "single-discipline",
                    "multidisciplinary",
                    "interdisciplinary",
                    "masters-doctor-same-field",
                    None,
                ],
            },

            # ✅ inline plan schema
            "plan1": plan_object_schema,
            "plan2": plan_object_schema,

            "instructionLanguage": {
                "type": "string",
                "enum": ["thai", "english", "both", "other"],
            },
            "instructionLanguageOther": {"type": ["string", "null"]},

            "admissionType": {
                "type": "null",

            },

            "isJointProgram": {"type": "boolean"},
            "jointInstitutionName": {"type": ["string", "null"]},

            "degreeConferralType": {
                "type": "string",
                "enum": ["single", "multiple"],
            },

            "curriculumYear": {"type": ["integer", "null"]},
            "openSemester": {"type": ["integer", "null"]},
            "openAcademicYear": {"type": ["integer", "null"]},

            "approvedByPolicyCommitteeMeetingNumber": {"type": ["string", "null"]},
            "approvedByPolicyCommitteeDate": {
                "type": ["string", "null"],
                "format": "date-time",
            },

            "approvedByUniversityCouncilMeetingNumber": {"type": ["string", "null"]},
            "approvedByUniversityCouncilDate": {
                "type": ["string", "null"],
                "format": "date-time",
            },

            "approvedByProfessionalCouncilMeetingNumber": {"type": ["string", "null"]},
            "approvedByProfessionalCouncilDate": {
                "type": ["string", "null"],
                "format": "date-time",
            },

            "careerPaths": {
                "type": "array",
                "items": {"type": "string"},
            },

            "instructionLocations": {
                "type": ["string", "null"],
                "enum": ["tha-phra-chan", "pattaya", "rangsit", "lampang", None],
            },

            "projectType": {
                "type": "string",
                "enum": ["normal", "special", "both"],
            },
            "isCostThaiStudent": {"type": "boolean"},
            "costThaiStudent": {"type": ["integer", "null"]},
            "isCostInternationalStudent": {"type": "boolean"},
            "costInternationalStudent": {"type": ["integer", "null"]},

            "nationalPolicyStrategy2561_2580": {"type": ["string", "null"]},
            "industry4_0Strategy2560_2579": {"type": ["string", "null"]},
            "sdgAlignment": {"type": ["string", "null"]},
            "institutionalAlignment": {"type": ["string", "null"]},
            "stakeholderExpectations": {"type": ["string", "null"]},

            "broadField": {"type": ["string", "null"]},
            "narrowField": {"type": ["string", "null"]},
            "detailField": {"type": ["string", "null"]},

            "remark": {"type": ["string", "null"]},
        },

        "required": [
            "curriculumId",
            "approvalStatus",
            "curriculumLevel",
            "curriculumFormat",
            "instructionLanguage",
            "admissionType",
            "isJointProgram",
            "degreeConferralType",
            "projectType",
            "isCostThaiStudent",
            "isCostInternationalStudent",
            "careerPaths",
            "plan1",
            "plan2",
        ],
    }

    master_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
            "approvalStatus": {
                "type": "string",
                "enum": ["approved", "in-progress", "rejected", "cancelled", "other"],
            },
            "institutionName": {"type": ["string", "null"]},
            "facultyName": {"type": ["string", "null"]},
            "facultyCode": {"type": ["string", "null"]},
            "approvalDate": {"type": ["string", "null"], "format": "date-time"},
            "startDate": {"type": ["string", "null"], "format": "date-time"},

            "curriculumCodeTh": {"type": ["string", "null"]},
            "curriculumNameTh": {"type": ["string", "null"]},
            "curriculumCodeEn": {"type": ["string", "null"]},
            "curriculumNameEn": {"type": ["string", "null"]},

            "degreeFullTh": {"type": ["string", "null"]},
            "degreeAbbrTh": {"type": ["string", "null"]},
            "degreeFullEn": {"type": ["string", "null"]},
            "degreeAbbrEn": {"type": ["string", "null"]},

            "majorsData": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "majorTh": {"type": ["string", "null"]},
                        "majorEn": {"type": ["string", "null"]},
                    },
                },
            },

            "curriculumLevel": {"type": "string", "enum": ["bachelor", "master", "doctor"]},
            "curriculumFormat": {
                "type": "string",
                "enum": ["continuing", "1-years", "2-years", "3-years", "4-years", "5-years", "6-years"],
            },

            "curriculumType": {
                "type": ["string", "null"],
                "enum": [
                    "academic",
                    "progressive-academic",
                    "professional",
                    "progressive-professional",
                    None,
                ],
            },
            "curriculumCategory": {
                "type": ["string", "null"],
                "enum": [
                    "single-discipline",
                    "multidisciplinary",
                    "interdisciplinary",
                    "masters-doctor-same-field",
                    None,
                ],
            },

            # ✅ INLINE: plan1
            "plan1": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "isPlan": {"type": "boolean"},
                    "isThesisOnly": {"type": "boolean"},
                    "isCourseworkAndThesis": {"type": "boolean"},
                    "isPlan11": {"type": "boolean"},
                    "isPlan12": {"type": "boolean"},
                    "isPlan21": {"type": "boolean"},
                    "isPlan22": {"type": "boolean"},
                },
                "required": [
                    "isPlan",
                    "isThesisOnly",
                    "isCourseworkAndThesis",
                    "isPlan11",
                    "isPlan12",
                    "isPlan21",
                    "isPlan22",
                ],
            },

            # ✅ INLINE: plan2
            "plan2": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "isPlan": {"type": "boolean"},
                    "isThesisOnly": {"type": "boolean"},
                    "isCourseworkAndThesis": {"type": "boolean"},
                    "isPlan11": {"type": "boolean"},
                    "isPlan12": {"type": "boolean"},
                    "isPlan21": {"type": "boolean"},
                    "isPlan22": {"type": "boolean"},
                },
                "required": [
                    "isPlan",
                    "isThesisOnly",
                    "isCourseworkAndThesis",
                    "isPlan11",
                    "isPlan12",
                    "isPlan21",
                    "isPlan22",
                ],
            },

            "instructionLanguage": {"type": "string", "enum": ["thai", "english", "both", "other"]},
            "instructionLanguageOther": {"type": ["string", "null"]},

            "admissionType": {"type": "null"},

            "isJointProgram": {"type": "boolean"},
            "jointInstitutionName": {"type": ["string", "null"]},

            "degreeConferralType": {"type": "string", "enum": ["single", "multiple"]},

            "curriculumYear": {"type": ["integer", "null"]},
            "openSemester": {"type": ["integer", "null"]},
            "openAcademicYear": {"type": ["integer", "null"]},

            "approvedByPolicyCommitteeMeetingNumber": {"type": ["string", "null"]},
            "approvedByPolicyCommitteeDate": {"type": ["string", "null"], "format": "date-time"},

            "approvedByUniversityCouncilMeetingNumber": {"type": ["string", "null"]},
            "approvedByUniversityCouncilDate": {"type": ["string", "null"], "format": "date-time"},

            "approvedByProfessionalCouncilMeetingNumber": {"type": ["string", "null"]},
            "approvedByProfessionalCouncilDate": {"type": ["string", "null"], "format": "date-time"},

            "careerPaths": {"type": "array", "items": {"type": "string"}},

            "instructionLocations": {
                "type": ["string", "null"],
                "enum": ["tha-phra-chan", "pattaya", "rangsit", "lampang", None],
            },

            "projectType": {"type": "string", "enum": ["normal", "special", "both"]},
            "isCostThaiStudent": {"type": "boolean"},
            "costThaiStudent": {"type": ["integer", "null"]},
            "isCostInternationalStudent": {"type": "boolean"},
            "costInternationalStudent": {"type": ["integer", "null"]},

            "nationalPolicyStrategy2561_2580": {"type": ["string", "null"]},
            "industry4_0Strategy2560_2579": {"type": ["string", "null"]},
            "sdgAlignment": {"type": ["string", "null"]},
            "institutionalAlignment": {"type": ["string", "null"]},
            "stakeholderExpectations": {"type": ["string", "null"]},

            "broadField": {"type": ["string", "null"]},
            "narrowField": {"type": ["string", "null"]},
            "detailField": {"type": ["string", "null"]},

            "remark": {"type": ["string", "null"]},
        },
        "required": [
            "curriculumId",
            "approvalStatus",
            "curriculumLevel",
            "curriculumFormat",
            "instructionLanguage",
            "admissionType",
            "isJointProgram",
            "degreeConferralType",
            "projectType",
            "isCostThaiStudent",
            "isCostInternationalStudent",
            "careerPaths",
            "plan1",
            "plan2",
        ],
    }


    return schema, prompt ,master_schema
