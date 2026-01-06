
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
    หมวดที่

    curr_course เป็นคำอธิบายตั้งต้นว่าหลักสูตรมีความพร้อมโดยอิงจากหลักเกณฑ์ใด(เอาข้อความส่วนมาทั้งหมด)

    (หมวดนี้อยู่ใน ด้านกายภาพ)
    physic_room จาก ห้องเรียน (เอาข้อความมาทั้งหมด หากเจอรายละเอียดแล้วมีการใช้ลำดับ เอาข้อความทั้งหมดมาเหมือนเดิมแต่ไม่เอาลำดับ แต่ให้ใช้ ',' คั่นแทน)
    physic_lab จาก ห้องปฏิบัติการ (เอาข้อความมาทั้งหมด หากเจอรายละเอียดแล้วมีการใช้ลำดับ เอาข้อความทั้งหมดมาเหมือนเดิมแต่ไม่เอาลำดับ แต่ให้ใช้ ',' คั่นแทน)
    physic_facility จาก สิ่งอํานวยความสะดวกเพื่อการเรียนรู้ (เอาข้อความมาทั้งหมด หากเจอรายละเอียดแล้วมีการใช้ลำดับ เอาข้อความทั้งหมดมาเหมือนเดิมแต่ไม่เอาลำดับ แต่ให้ใช้ ',' คั่นแทน หากมีการอธิบายลักษณะแยกย่อยของที่มีให้เอามาแค่โดยรวม เช่น หนังสือ หากแยกย่อยไปว่าเป็นภาษาไทย อังกฤษ ให้เอามาแค่หนังสือรวม)
    physic_other จาก ความพร้อมด้านกายภาพ อื่น ๆ (เอาข้อความทั้งหมดมา นิกจากหัวข้อกายภาพอื่นๆ หากมีหัวข้อที่ไม่ได้อยู่ใน ห้องเรียน, ห้องปฏิบัติการ และ สิ่งอํานวยความสะดวกเพื่อการเรียนรู้ ให้เอามาใส่ในหมวดนี้ด้วยเลย)

    (หมวดนี้อยู่ใน ด้านวิชาการ ในนี้จะเป็ตาราง ซึ่งตารางมี 3 row ซึ่ง row แรก คือ จํานวนผลงานทางวิชาการ ซึ่งมี 3 row ย่อย row สอง คือ จํานวนอาจารย์ประจําหลักสูตร (คน) row สาม คือ สัดส่วนอาจารย์:ผลงาน ซึ่งมี 2 row ย่อย)
    (ในหัวข้อย่อย จํานวนผลงานทางวิชาการ)
    count_research จากหัวข้อ งานวิจัยหรือบทความวิจัย (ชิ้น) (เอามาแค่จำนวน)
    count_academic_paper จากหัวข้อ ผลงานทางวิชาการอื่น ๆ เช่น ตํารา หนังสือ/บทความวิชาการอื่น ๆสิ่งประดิษฐ์ เป็นต้น(ชิ้น) (เอามาแค่ผลรวมจำนวน)
    sum_research_academic จากหัวข้อ รวมผลงานทางวิชาการทั้งหมด (ชิ้น) (เอามาแค่จำนวน)
    (ในหัวข้อย่อย จํานวนอาจารย์ประจําหลักสูตร (คน))
    count_full_lecturer จากหัวข้อ จํานวนอาจารย์ประจําหลักสูตร (คน) (เอามาแค่จำนวน)
    (ในหัวข้อย่อย สัดส่วนอาจารย์ : ผลงาน)
    ratio_research จากหัวข้อ วิจัย (เอามาทั้งอัตราส่วน ถ้าเป็น 0 ก็ใส่ 0:0)
    ratio_other จากหัวข้อ อื่น ๆ (เอามาทั้งอัตราส่วน ถ้าเป็น 0 ก็ใส่ 0:0)
    ratio_sum จากหัวข้อ รวม (เอามาทั้งอัตราส่วน ถ้าเป็น 0 ก็ใส่ 0:0)

    (หมวดนี้อยู่ใน ด้านการเงินและการบัญชี)
    (ประมาณการรายได้และค่าใช้จ่ายนักศึกษาของหลักสูตร)
    income (งบประมาณรายรับ หากมีหลายปีให้เอาปีที่มากที่สุด)
        detail_income รายละเอียดรายรับ
        amount_income ราคารายละเอียดรายรับ (เอามาแค่ตัวเลข)
    outcome (งบประมาณรายจ่าย หากมีหลายปีให้เอาปีที่มากที่สุด)
        detail_outcome รายละเอียดรายจ่าย
        amount_outcome ราคารายละเอียดรายจ่าย (เอามาแค่ตัวเลข)
    (วิเคราะห์ความคุ้มทุนของหลักสูตร)
    sum_income_person รายได้ต่อคน (เอามาแค่ตัวเลข หากมีหลายปีให้เอาปีที่มากที่สุด)
    sum_outcome_person ค่าใช้จ่ายผันแปรต่อคน (เอามาแค่ตัวเลข หากมีหลายปีให้เอาปีที่มากที่สุด)
    roi_minimum_collegian จำนวนนักศึกษาที่คุ้มทุน (เอามาแค่ตัวเลข หากมีหลายปีให้เอาปีที่มากที่สุด)

    (หมวดนี้อยู่ใน ด้านการบริหารจัดการ)
    sum_lecturer จํานวนอาจารย์(ประจำ/พิเศษ) (เอามาแค่เลข ผลรวม)
    sum_staff จํานวนเจ้าหน้าที่ (เอามาแค่เลข)
    improve_evaluate การพัฒนาทักษะการจัดการเรียนการสอนและการประเมินผล (หรือ'สายวิชาการ' เอามาทั้งหมด โดยเอามาจาก การพัฒนาความรู้และทักษะให้แก่อาจารย์)
    improve_profession การพัฒนาทักษะด้านวิชาการและวิชาชีพ (หรือ'สายสนับสนุน' เอามาทั้งหมด โดยเอามาจาก การพัฒนาความรู้และทักษะให้แก่อาจารย์)

    (หมวดนี้อยู่ใน อาจารย์ผู้รับผิดชอบหลักสูตรและอาจารย์ประจําหลักสูตร)
    lecturer (เป็นตารางที่หัวตารางจะมีเรื่อง ลําดับที่ ตำแหน่งทางวิชาการ ชื่อ-สกุล คุณวุฒิ สาขาวิชา สถาบัน ปีพ.ศ. บางทีอาจะมี ใบอนุญาตเป็นผู้ประกอบวิชาชีพ)
    lecturer_qualification ตำแหน่งทางวิชาการ
    lecturer_name ชื่อ-สกุล
    lecturer_type ประเภทอาจารย์ (เป็นได้ อาจารย์ผู้รับผิดชอบหลักสูตร หรือ อาจารย์ประจําหลักสูตร ให้ดูใต้สุดของตาราง บางทีมีการบอกว่า อาจารย์ลำดับที่เท่าไหร่บ้างเป็นอาจารย์ผู้รับผิดชอบหลักสูตร หากไม่มีบอกให้ตั้งทุกค่าเป็น อาจารย์ผู้รับผิดชอบหลักสูตร)
    lecturer_detail (รายละเอียดของอาจารย์)
        lecturer_degree คุณวุฒิ
        lecturer_university สถาบัน
        lecturer_graduate ปี พ.ศ.
    """


    schema = {
        "type": "object",
        "properties": {
            "curr_course": {"type": ["string", "null"]},
            "physic_room": {"type": ["string", "null"]},
            "physic_facility": {"type": ["string", "null"]},
            "physic_lab": {"type": ["string", "null"]},
            "physic_other": {"type": ["string", "null"]},
            "count_research": {"type": ["integer", "null"]},
            "count_academic_paper": {"type": ["integer", "null"]},
            "sum_research_academic": {"type": ["integer", "null"]},
            "count_full_lecturer": {"type": ["integer", "null"]},
            "ratio_research": {"type": ["string", "null"]},
            "ratio_other": {"type": ["string", "null"]},
            "ratio_sum": {"type": ["string", "null"]},

            "income": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "detail_income": {"type": ["string", "null"]},
                        "amount_income": {"type": ["number", "null"]},
                    },
                    "required": ["detail_income", "amount_income"],
                    "additionalProperties": False,
                },
            },

            "outcome": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "detail_outcome": {"type": ["string", "null"]},
                        "amount_outcome": {"type": ["number", "null"]},
                    },
                    "required": ["detail_outcome", "amount_outcome"],
                    "additionalProperties": False,
                },
            },

            "sum_income_person": {"type": ["number", "null"]},
            "sum_outcome_person": {"type": ["number", "null"]},
            "roi_minimum_collegian": {"type": ["string", "null"]},
            "sum_lecturer": {"type": ["integer", "null"]},
            "sum_staff": {"type": ["integer", "null"]},
            "improve_evaluate": {"type": ["string", "null"]},
            "improve_profession": {"type": ["string", "null"]},

            "lecturer": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "lecturer_name": {"type": ["string", "null"]},
                        "lecturer_qualification": {"type": ["string", "null"]},
                        "lecturer_type": {"type": ["string", "null"]},
                        "lecturer_detail": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "lecturer_degree": {"type": ["string", "null"]},
                                    "lecturer_university": {"type": ["string", "null"]},
                                    "lecturer_graduate": {"type": ["integer", "null"]},
                                },
                                "required": [],
                                "additionalProperties": False,
                            },
                            "required": [],
                        },
                    },
                    "required": ["lecturer_name","lecturer_type","lecturer_detail"],
                    "additionalProperties": False,
                },
            },
        },
        "required": [],
        "additionalProperties": False,
    }

    return schema, prompt