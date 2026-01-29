def schema_prompt(chunk_pdf_bytes: bytes = None):


    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจาก หมวดที่ 6 เท่านั้น

curriculumId null

breakEvenAnalysis จากหัวข้อ วิเคราะห์ความคุ้มทุนของหลักสูตร (หากมีหลายปี ให้เอาเลขปีที่น้อยที่สุด)
    revenuePerStudent รายรับต่อคนตลอดหลักสูตร
    costPerStudent ค่าใช้จ่ายต่อคนตลอดหลักสูตร
    breakEvenStudentCount จำนวนนักศึกษาน้อยสุดที่คุ้มทุน

managementReadiness จากหัวข้อ ด้านการบริหารจัดการ
    lecturerCount จํานวนอาจารย์ (หากมีอาจารย์ทั้ง ประจำ พิเศษ หรือ อื่นๆ ให้รวมกันเป็นค่าเดียว)
    staffCount จํานวนเจ้าหน้าที่
    teachingSkillDevelopment การพัฒนาทักษะการจัดการเรียนการสอนและการประเมินผล (จากหัวข้อย่อย การพัฒนาความรู้และทักษะให้แก่อาจารย์)
    professionalSkillDevelopment การพัฒนาทักษะด้านวิชาการและวิชาชีพ (จากหัวข้อย่อย การพัฒนาความรู้และทักษะให้แก่อาจารย์)

จากหัวข้อ อาจารย์ผู้รับผิดชอบหลักสูตรและอาจารย์ประจําหลักสูตร
courseLecturers (เป็นตารางที่มี 6 column ลำดับที่ 'ตำแหน่งทางวิชาการ' ,'ชื่อ - สกุล' ,'คุณวุฒิ' ,'สาขาวิชา' ,'สำเร็จการศึกษา' บางทีอาจมี column อื่นบ้างเช่น 'ใบอนุญาตเป็น' อันนั้นไม่ต้องสนใจ โดย 'สำเร็จการศึกษา' มี 2 column ย่อย 'สถาบัน' และ 'ปี พ.ศ.' ปล. ในบางครั้งท้ายตาราง จะมีการบอกว่าอาจารย์ตั้งแต่ ลำดับที่ 1 ถึง เลขใดๆ เป็นอาจารย์ผู้รับผิดชอบหลักสูตร หากไม่มีการบอกให้คิดว่าอาจารย์ทุกคนเป็นผู้รับผิดชอบหลักสูตร)
  position 'ตำแหน่งทางวิชาการ'
  fullName 'ชื่อ - สกุล'
  courseRole ตอบ 1 หากเป็นอาจารย์ผู้รับผิดชอบหลักสูตร หรือ ตอบ 2 หากไม่ได้เป็นอาจารย์ผู้รับผิดชอบหลักสูตร
  qualifications (รายละเอียดการศึกษาของอาจารย์ บางทีละเอียดของแต่ละ column จะรวมเป็นอันเดียวของแต่ละ column เช่น อาจารย์ มี 3 คุณวุติ บางตาราง ทั้ง 3 คุณวุฒิจะอยู่ช่องเดียวกัน บางอันแต่ละ คุณวุฒิจะอยู่คนละช่องกัน จะมี column อื่นมาคั่น คุณวุติ)
    degree 'คุณวุฒิ'
    major 'สาขาวิชา'
    institute 'สถาบัน'
    graduationYearBe 'ปี พ.ศ.'
    """

    schema = {
        "type": "object",
        "properties": {
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
                        "position": {"type": ["string", "null"]},
                        "fullName": {"type": ["string", "null"]},
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
        "additionalProperties": False,
        "required":["breakEvenAnalysis","managementReadiness","courseLecturers"]
    }

    return schema, prompt
