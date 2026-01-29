def schema_prompt(chunk_pdf_bytes: bytes = None):

    prompt = """
        จากเนื้อหาในไฟล์ PDF (เรียงจากบนลงล่าง)
        ❗ ห้ามอธิบายเพิ่มเติม
        ❗ ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด

        หมวดที่ 5

        1. การพัฒนาคุณลักษณะของนักศึกษา
        - generalCharacteristics: คุณลักษณะทั่วไป + PLO ที่เกี่ยวข้อง
        - professionalCharacteristics: คุณลักษณะด้านวิชาชีพ + PLO ที่เกี่ยวข้อง

        2. ความสอดคล้อง PLO กับมาตรฐาน (Bloom / Generic / Specific)
        - ระบุ PLO
        - ระบุ domain และ level ของ Bloom
        - ติ๊ก true / false ให้ครบ

        3. กลยุทธ์การสอนและการประเมินผลตาม PLO

        4. Curriculum Mapping
        - แยกตามกลุ่มวิชา
        - รายวิชา / หน่วยกิต / ชั้นปี
        - ระบุ PLO ที่เชื่อมโยงเป็น true/false

        5. ความคาดหวังผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา

        6. การฝึกประสบการณ์ภาคสนาม (ถ้ามี)

        7. โครงงาน / วิจัย / วิทยานิพนธ์ (ถ้ามี)
        """

    prompt = """เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
ข้อมูลจากหมวดที่ 5

curriculumId เป็น null


จากหัวข้อ ความคาดหวังของผลลัพธBการเรียนรู้เมื่อสิ้นปีการศึกษา
head_plos_yearEndLearningOutcomeExpectations ค่าคอลัมจาก column ย่อยของ'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' (จะเป็นรหัสเช่น plo-1 ,A1 ,K3)
yearEndLearningOutcomeExpectations (ตารางที่มี 3 column หลัก 'ชั้นปี' ,'ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา' และ'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ซึ่ง 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะมี column ย่อย เป็นรหัส เช่น 'PLO1' ,'PLO-4' ,'S3' แต่บางครั้ง จะมีแค่ column ย่อย 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะไม่มี โดย 'ชั้นปี' จะมีหลาย 'ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา')
  yearLevel 'ชั้นปี' (หากไม่มีรายละเอียดเพิ่มเติมเอามาแค่เลข แต่หากมีคำว่า '(สหกิจศึกษา)' ให้เติม 0 ด้านหลัง และ หากมีคำว่า '(โครงงานพิเศษ)' ให้เติม 1 ด้านหลัง)
  expectations
    expectation 'ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา'
    plos มาจาก column ย่อยใน 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ทั้งหมด โดยหาก ค่าจาก column ย่อยนั้นมีค่าให้ใส่ ชื่อ column ย่อยนั้นมา

fieldExperience จากหัวข้อ องค์ประกอบเกี่ยวกับประสบการณ์ภาคสนาม (การฝึกงาน หรือสหกิจศึกษา)
  period ช่วงเวลา
  preparation การเตรียมการ
  assessment การประเมินผล

projectResearchRequirement จากหัวข้อ ข้อกำหนดเกี่ยวกับการทำโครงงาน หรือ งานวิจัย
  period ช่วงเวลา
  preparation การเตรียมการ
  assessment การประเมินผล
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},


            "head_plos_yearEndLearningOutcomeExpectations":{"type":["array"]},
            "yearEndLearningOutcomeExpectations": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "yearLevel": {"type": ["integer", "null"]},
                        "expectations": {
                            "type": ["array"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "expectation": {"type": ["string"]},
                                    "plos": {
                                        "type": ["array"],
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            },
            "fieldExperience": {
                "type": ["object", "null"],
                "properties": {
                    "period": {"type": ["string", "null"]},
                    "preparation": {"type": ["string", "null"]},
                    "assessment": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },

            "projectResearchRequirement": {
                "type": ["object", "null"],
                "properties": {
                    "period": {"type": ["string", "null"]},
                    "preparation": {"type": ["string", "null"]},
                    "assessment": {"type": ["string", "null"]}
                },
                "additionalProperties": False
            },
        
            },
        "additionalProperties": False,
        "required":["yearEndLearningOutcomeExpectations"]
        }
    

    return schema, prompt
