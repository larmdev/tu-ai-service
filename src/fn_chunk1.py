def schema_prompt(chunk_pdf_bytes: bytes | None = None):

    prompt = """
    จากไฟล์ PDF ที่ให้มา ให้ทำการ extract ข้อมูลโดยเรียงจากบนลงล่างตามลำดับที่ปรากฏในเอกสาร
    ห้ามอธิบาย ห้ามใส่ข้อความอื่นใด
    ให้ตอบเป็น JSON อย่างเดียว และต้องเป็นไปตามโครงสร้างที่กำหนดเท่านั้น
    หากไม่พบข้อมูล ให้ใส่ค่าเป็น null หรือ false ตามชนิดข้อมูล
    curriculumId ให้ค่าเป็น null
    approvalStatus ให้ค่าเป็น in-progress
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

            "degreeAbbrTh": {"type": ["string", "null"]},
            "degreeFullTh": {"type": ["string", "null"]},
            "degreeAbbrEn": {"type": ["string", "null"]},
            "degreeFullEn": {"type": ["string", "null"]},

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
                "type": "string",
                "enum": [
                    "thai-only",
                    "thai-and-international",
                    "thai-and-international-with-thai-proficiency",
                ],
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

    return schema, prompt
