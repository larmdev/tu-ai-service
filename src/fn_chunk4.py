
def schema_prompt(chunk_pdf_bytes: bytes=None):

    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
    หมวดที่ 4 ไม่ถึง คำอธิบายรายวิชา

    max_semester จาก ระยะเวลาการศึกษาสูงสุด ให้เอามาแค่เลข

    (ในบางหมวดจะมีให้ติ๊กเลือก วิธีหากไม่รู้ว่าเลือกค่าใดส่วนมากจะเป็นตัวที่ถูกเลือกค่าเดียวในแต่ละหมวด แต่หากถูกเลือกหลายค่าให้ใส่ ',' คั่น)
    day_class จาก วัน-เวลา ในการดําเนินการเรียนการสอน หมวดที่เจอคำคล้ายๆว่า 'วัน – เวลาราชการปกติ หรือนอกวัน – เวลาราชการ' (ส่วนมากจะเป็นช่องให้ติ๊ก เอามาเฉพาะค่าที่ถูกเลือก)

    detail_day_class (รวมรายละเอียดช่วงเวลาเรียนของภาคการศึกษาทั้งหมด)
    type_day_class ภาคการศึกษาที่เปิดเรียน (เช่น ภาคการศึกษาที่ 1 ,ที่ 2 ,ภาคฤดูร้อน)
    detail_type_day_class (รายละเอียดช่วงเวลาเรียนของแต่ละภาคการศึกษา)
        start_class เดือนเริ่มต้นของภาคการศึกษานั้น (เอามาแค่เดือน)
        end_class เดือนสิ้นสุดของภาคการศึกษานั้น (เอามาแค่เดือน)

    type_class จาก ระบบการศึกษา หมวดที่เจอคำคล้ายๆว่า 'แบบชั้นเรียน (Onsite) หรือแบบทางไกล (Online)' (ส่วนมากจะเป็นช่องให้ติ๊ก เอามาเฉพาะค่าที่ถูกเลือก)

    (ต่อไปจะเป็นรายละเอียดหน่วยกิตทั้งหมด หากมีรูปแบบหน่วยกิตหลายรูปแบบเอามาแค่รูปแบบเดียว)
    total_credits จํานวนหน่วยกิตรวมตลอดหลักสูตร (เอามาแค่เลข)

    detail_credit (รายละเอียดการแจกแจงของหน่วยกิตรวมทั้งหมด)
    main (รายละเอียดการของหน่วยกิตแต่ละประเภท)
        value_main หมวดที่เป็น รายละเอียดหลักของหน่วยกิตรวม หมวดที่มักมีคำคล้ายๆว่า 'หมวดวิชาศึกษาทั่วไป หรือ วิชาเฉพาะ หรือ วิชาเลือกเสรี' (และอาจเป็นค่าอื่นๆได้ ส่วนมากจะมี ลำดับของ ว่า เป็น 1,2,3 แต่ไม่เอารายละเอียดของลำดับนั้น โดยให้เอามาแค่ชื่อไม่ต้องเอาลำดับมา)
        credit_main จำนวนหน่วยกิตของหมวดหลัก
        detail_main (รายละเอียดของหมวด)
        sub_main (หมวดย่อยของหมวดหลัก หากมีค่า เป็น 1.1 1.2 2.1 2.2 แต่ถ้าลึกเข้าไปสองขั้นเช่น 2.1.1 2.2.1 อย่างงี้ไม่เอา)
            value_sub_main ชื่อหมวดย่อย (เอามาแค่ชื่อไม่ต้องเอาลำดับมา)
            credit_sub_main จำนวนหน่วยกิตของหมวดย่อยนั้น

    (ต่อไปจะเป็นรายละเอียดวิชาที่มีทั้งหมด)
    course (เก็บรายวิชาทั้งหมดที่มี)
        course_type รายวิชานี้อยู่ในหมวดใดของโครงสร้างหลักสูตร(ค่าต้องอยู่ใน detail_credit["main"]["value_main"] เท่านั้น และเอามาแค่ค่าเท่านั้นไม่ต้องเอาลำดับมา)
        sub_course_type รายวิชานี้อยู่ในหมวดย่อย ของหมวดหลัก ใดของโครงสร้างหลักสูตร (ค่าต้องอยู่ใน detail_credit["main"]["detail_main"]["value_sub_main"] ที่อยู่ใน detail_credit["main"]["value_main"] เดียวกันเท่านั้น ส่วนมาก "value_main" มีอยู่ลำดับต้นเช่น 1. 2. "value_sub_main" จะเป็นหัวข้อย่อยเช่น 1.1  2.2 2.3 และเอามาแค่ค่าเท่านั้นไม่ต้องเอาลำดับมา)
        thai_abv ชื่อรหัสวิชาย่อ ภาษาไทย (format ให้เป็น ตัวย่อภาษาไทย. เลข ในกรณีที่ตัวอักษรกับภาษาแยกกันชัดเจน หากแยกกันไม่ชัดเจนให้ตัวติดกันให้หมด)
        th_name ชื่อวิชาเต็ม ภาษาไทย
        credit จำนวนหน่วยกิตเต็มของรายวิชานั้น (เอามาแค่ตัวเลข)
        credit_detail รายละเอียดของหน่วยกิตรายวิชา (ส่วนมากจะเป็น (เลข-เลข-เลข) บางกรณีอาจเป็น (มากกว่า เลข ชั่วโมง) format ที่ให้เก็บให้เติม '()'ครอบทั้งหมดด้วยหากไม่มี)
        eng_abv ชื่อรหัสวิชาย่อ ภาษาอังกฤษ (format ให้เป็น ตัวย่อภาษาอังกฤษ เลข ในกรณีที่ตัวอักษรกับภาษาแยกกันชัดเจน หากแยกกันไม่ชัดเจนให้ตัวติดกันให้หมด)
        eng_name ชื่อวิชาเต็ม ภาษาอังกฤษ
    """

    schema = {
        "type": "object",
        "properties": {

            "max_semester": {"type": ["string", "null"]},

            "day_class": {"type": ["string", "null"]},
            "detail_day_class": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "type_day_class": {"type": ["string", "null"]},
                        "detail_type_day_class": {
                            "type": ["object", "null"],
                            "properties": {
                                "start_class": {"type": ["string", "null"]},
                                "end_class": {"type": ["string", "null"]},
                            },
                            "required": ["start_class","end_class"],
                        },
                    },
                    "required": ["type_day_class", "detail_type_day_class"],
                },
            },

            "type_class": {"type": ["string", "null"]},

            "total_credits": {"type": ["integer", "null"]},
            "detail_credit": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "main": {
                            "type": ["object", "null"],
                            "properties": {
                                "value_main": {"type": ["string"]},
                                "credit_main": {"type": ["number"]},
                                "detail_main": {
                                    "type": ["object"],
                                    "properties": {
                                        "sub_main": {
                                            "type": ["array", "null"],
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "value_sub_main": {"type": ["string", "null"]},
                                                    "credit_sub_main": {"type": ["number", "null"]},
                                                },
                                                "required": ["value_sub_main", "credit_sub_main"],
                                            },
                                        },
                                    },
                                    "required": [],
                                },
                            },
                            "required": ["value_main","detail_main"],
                        },
                    },
                    "required": [],
                },
            },
            
            "course": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "course_type": {"type": ["string", "null"]},
                        "sub_course_type": {"type": ["string", "null"]},
                        "thai_abv": {"type": ["string", "null"]},
                        "th_name": {"type": ["string", "null"]},
                        "credit": {"type": ["number", "null"]},
                        "credit_detail": {"type": ["string", "null"]},
                        "eng_abv": {"type": ["string", "null"]},
                        "eng_name": {"type": ["string", "null"]},
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
        },
        "required": [],
    }

    return schema, prompt