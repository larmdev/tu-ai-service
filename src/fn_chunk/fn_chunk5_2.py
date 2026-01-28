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
head_plos ค่าคอลัมจาก column ย่อยของ'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' (จะเป็นรหัสเช่น plo-1 ,A1 ,K3)
curriculumMapping (ตารางที่มี 4 column หลัก 'รายวิชา / ชุดวิชา และ หน่วยกิต' ,'หน่วยกิต' ,'ชั้นปีที่' และ'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ซึ่ง 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะมี column ย่อย เป็นรหัส เช่น 'PLO1' 'PLO-4' 'S3' แต่บางครั้ง จะมีแค่ column ย่อย 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' จะไม่มี)
  courseGroup ข้อความนั้น ไม่ใช่รหัสรายวิชา ส่วนมาก จะเป็นที่ขึ้นต้นด้วยคำว่า "หมวด", "วิชา" หรือ "กลุ่มวิชา" โดยแถวนั้นจะไม่มีค่าอะไรเลยนอกจากในบรรทัด'
  courses
    subCourseGroup 'รายวิชา / ชุดวิชา และ หน่วยกิต' (เป็นค่าที่รหัสรายวิชา และชื่อรายวิชา)
    credits 'หน่วยกิต' (ค่าจาก 'หน่วยกิต' เป็น format 3(3-0-6) ,3 ,3 (570 ชั่วโมง) เอามาแค่เลขเดี่ยวๆด้านหน้าวงเล็บ)
    yearLevel 'ชั้นปีที่' 
    plos มาจาก column ย่อยใน 'ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)' ทั้งหมด โดยหาก ค่าจาก column ย่อยนั้นมีค่าให้ใส่ ชื่อ column ย่อยนั้นมา
    """

    schema = {
        "type": "object",
        "properties": {
            "curriculumId": {"type": ["string", "null"]},
            "head_plos":{"type":["array","null"]},
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
                                    "yearLevel": {"type": ["integer"]},
                                    "plos": {
                                        "type": ["array", "null"],
                                    }
                                },
                                "additionalProperties": False,
                                "required": ["subCourseGroup","credits","yearLevel","plos"]
                            }
                        }
                    },
                    "additionalProperties": False,
                    "required": ["courseGroup"]
                }
            },
        },
        "additionalProperties": False,
        "required":["curriculumMapping"]
    }

    return schema, prompt
