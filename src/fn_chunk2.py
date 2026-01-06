
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
        หมวดที่ 2

        student_nation_id จาก การรับเข้าศึกษา (ส่วนมากจะเป็นช่องให้ติ๊ก เอามาเฉพาะค่าที่ถูกเลือก ค่าที่ถูกเลือกมาจากค่าเดียวที่แตกต่างจากค่าอื่น)

        qualification_collegian จาก คุณสมบัติของผู้เข้าศึกษา (เอาทั้งหมด ตั้งแต่คุณสมบัติเป็นไปตามข้อบังคับมหาลัย หากมีรายละเอียดหลายข้อให้ วงเล็บ '{ }' คลุมตั้งแต่ข้อ 1 ถึงรายละเอียดข้อสุดท้าย ในส่วนของรายละเอียดทั้งหมดนั้นให้เอา และรายละเอียดแต่ละข้อในนั้น คั่นด้วย ',')

        selection_collegian จาก การคัดเลือกผู้เข้าศึกษา 

        (ต่อไปเป็นจาก 2.3แผนการรับนักศึกษาและผู้สําเร็จการศึกษาในระยะ 5 ปี)
        admit_per_year จาก ในแต่ละปีการศึกษาจะรับนักศึกษาปีละ (เอามาแค่เฉพาะเลข)

        (ต่อไปเป็นตาราง มีหัวข้อ จำนวนนักศึกษา และ จํานวนนักศึกษาแต่ละปีการศึกษา ซึ่งใน จํานวนนักศึกษาแต่ละปีการศึกษา ก็จะแตกออกเป็นหัวข้อย่อยต่างๆ จะเป็นปีการศึกษา)
        year_admit (เป็นตัวแปรที่เก็บค่าของตารางทั้งหมด หากบางค่า เป็น 0 หรือ - มาก็ก็ให้เป็น)
        header_year_admit น่าคือหัวตางที่เป็นหัวข้อย่อยทั้งหมดของ (จํานวนนักศึกษาแต่ละปีการศึกษา)
        year_level (เก็บแต่ละแถวของตาราง)
            value_year_level แถวซึ่งเป็นค่าจาก หัวข้อ จำนวนนักศึกษา
            count เลขของแต่ละหัวข้อย่อย จํานวนนักศึกษาแต่ละปีการศึกษา (เติมให้ให้มีจำนวนสมาชิกเท่ากับ header_year_admit ซึ่งตารางมักเติมฝั่งขวาเต็มก่อนเสมอ หมายถึงปีท้ายๆถูกเติมก่อนเสมอ) 
        year_sum เลขของแต่ละหัวข้อย่อย จํานวนนักศึกษาแต่ละปีการศึกษา ใน หัวข้อ จำนวนนักศึกษา มีค่าคือ 'รวม' (เติมให้ให้มีจำนวนสมาชิกเท่ากับ header_year_admit)
        year_expect_graduate เลขของแต่ละหัวข้อย่อย จํานวนนักศึกษาแต่ละปีการศึกษา ใน หัวข้อ จำนวนนักศึกษา มีค่าคือ 'คาดว่าจะจบการศึกษา' (เติมให้ให้มีจำนวนสมาชิกเท่ากับ header_year_admit)

        freshy_problem จากหัวข้อ ปัญหาของนักศึกษาแรกเข้า (เอามาทั้งหมดเอาเลขข้อมาด้วย แต่ให้เติม ',' คั่นข้อที่เปลี่ยนไป)

        repair_freshy_problem จากหัวข้อ กลยุทธ์ในการดําเนินการเพื่อแก้ไขปัญหา/ข้อจํากัดของนักศึกษาในข้อ 2.4 (เอามาทั้งหมดเอาเลขข้อมาด้วย แต่ให้เติม ',' คั่นข้อที่เปลี่ยนไป)
    """

# มีตัวแปรซ้ำ: year_level

    schema = {
        "type": "object",
        "properties": {
            "student_nation_id": {"type": ["string", "null"]},
            "qualification_collegian": {"type": ["string", "null"]},
            "selection_collegian": {"type": ["string", "null"]},
            "admit_per_year": {"type": ["string", "null"]},
            "year_admit": {
                "type": ["object", "null"],
                "properties": {
                    "header_year_admit": {
                        "type": ["array"],
                        "items": {"type": ["string"]},
                    },
                    "year_level": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "value_year_level": {"type": ["string"]},
                                "count": {
                                    "type": ["array"],
                                    "items": {"type": ["integer", "null"]},
                                },
                            },
                            "required": ["value_year_level","count"],
                            "additionalProperties": False,
                        },
                    },
                    "year_sum": {
                        "type": ["array", "null"],
                        "items": {"type": ["integer", "null"]},
                    },
                    "year_expect_graduate": {
                        "type": ["array", "null"],
                        "items": {"type": ["integer", "null"]},
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "freshy_problem": {"type": ["string", "null"]},
            "repair_freshy_problem": {"type": ["string", "null"]},
        },
        "required": [],
        "additionalProperties": False,
    }


    return schema, prompt