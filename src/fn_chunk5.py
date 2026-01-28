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

จากหัวข้อ แผนที่แสดงการกระจายความรับผิดชอบผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) สู่รายวิชา (Curriculum Mapping)
curriculumMapping (ตารางที่มี 4 column หลัก 'รายวิชา / ชุดวิชา และ หน่วยกิต' ,'หน่วยกิต' ,'ชั้นปีที่' และ'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ซึ่ง 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะมี column ย่อย เป็นรหัส เช่น 'PLO1' 'PLO-4' 'S3' แต่บางครั้ง จะมีแค่ column ย่อย 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะไม่มี)
  courseGroup ค่าจาก 'รายวิชา / ชุดวิชา และ หน่วยกิต' (แต่จะมีความพิเศษตรงที่ ข้อความนั้น ไม่ใช่หัสรายวิชา ส่วนมาก จะเป็นที่ขึ้ต้นด้วยคำว่า 'หมวด', 'วิชา' หรือ 'กลุ่มวิชา' โดยแถวนั้นจะไม่มีค่าอะไรเลยนอกจากใน 'รายวิชา / ชุดวิชา และ หน่วยกิต')
  courses
    subCourseGroup 'รายวิชา / ชุดวิชา และ หน่วยกิต' (เป็นค่าที่รหัสรายวิชา และชื่อรายวิชา)
    credits 'หน่วยกิต' (หากมีค่ารายละเอียดของหน่วยกิต เช่น 3(3-0-9) หรือ 3(มากกว่า 570 ชั่วโมง) เอามาแค่เลขหน้าวงเล็บ จากตัวอย่างคือ 3 หากไม่มีให้เป็น 0)
    yearLevel 'ชั้นปีที่' (เป็นได้ 1ถึง4 หากมีรายละเอียดของชั้นปี เช่น 3/2 หรือ 3-2 เราจะไม่เอา รายละเอียด คือจะเอาแค่เลขด้านหน้า)
    plos มี additionalProperties key คือ columns ย่อยของ 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ทั้งหมด (ซึ่งหาก ช่องไหนมีค่าให้ ส่ง true อันไหนไม่มีค่าให้ false)
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},

            "curriculumMapping": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "courseGroup": {"type": ["string"]},
                        "courses": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "subCourseGroup": {"type": ["string", "null"]},
                                    "credits": {"type": ["integer"]},
                                    "yearLevel": {"type": ["integer", "null"]},
                                    "plos": {
                                        "type": ["object", "null"],
                                        "additionalProperties": {"type": ["boolean", "null"]}
                                    }
                                },
                                "additionalProperties": False
                            }
                        }
                    },
                    "additionalProperties": False
                }
            },
        },
        "additionalProperties": False,
        "required":["curriculumMapping"]
    }

    return schema, prompt
