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
ข้อมูลจากหมวดที่ 6

curriculumId

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

breakEvenAnalysis จากหัวข้อ วิเคราะห์ความคุ้มทุนของหลักสูตร (หากมีหลายปี ให้เอาเลขปีที่น้อยที่สุด)
revenuePerStudent รายรับต่อคนตลอดหลักสูตร
costPerStudent ค่าใช้จ่ายต่อคนตลอดหลักสูตร
breakEvenStudentCount จำนวนนักศึกษาน้อยสุดที่คุ้มทุน

managementReadiness จากหัวข้อ ด้านการบริหารจัดการ
    lecturerCount จํานวนอาจารย์ (หากมีอาจารย์ทั้ง ประจำ พิเศษ หรือ อื่นๆ ให้รวมกันเป็นค่าเดียว)
    staffCount จํานวนเจ้าหน้าที่
    จากหัวข้อย่อย การพัฒนาความรู้และทักษะให้แก่อาจารย์
    teachingSkillDevelopment การพัฒนาทักษะการจัดการเรียนการสอนและการประเมินผล
    professionalSkillDevelopment การพัฒนาทักษะด้านวิชาการและวิชาชีพ

จากหัวข้อ อาจารย์ผู้รับผิดชอบหลักสูตรและอาจารย์ประจําหลักสูตร
courseLecturers (เป็นตารางที่มี 6 column ลำดับที่
'ตำแหน่งทางวิชาการ' ,'ชื่อ - สกุล' ,'คุณวุฒิ' ,'สาขาวิชา' ,'สำเร็จการศึกษา' บางทีอาจมี column อื่นบ้างเช่น 'ใบอนุญาตเป็น' อันนั้นไม่ต้องสนใจ โดย 'สำเร็จการศึกษา' มี 2 column ย่อย 'สถาบัน' และ 'ปี พ.ศ.' ปล. ในบางครั้งท้ายตาราง จะมีการบอกว่าอาจารย์ตั้งแต่ ลำดับที่ 1 ถึง เลขใดๆ เป็นอาจารย์ผู้รับผิดชอบหลักสูตร หากไม่มีการบอกให้คิดว่าอาจารย์ทุกคนเป็นผู้รับผิดชอบหลักสูตร)
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
        "additionalProperties": False
    }

    return schema, prompt
