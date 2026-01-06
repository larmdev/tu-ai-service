
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
        หมวดที่ 3 

        curr_philosophy จาก ปรัชญาการศึกษา (ให้เอามาทั้งหมด),

        curr_objective จาก วัตถุประสงค์ของหลักสูตร (ให้เอาทั้งหมด ให้ใช้ ',' คั่นข้อ),

        (หากในข้อมูลมี plo แล้วไม่ต้องสนใจค่าอื่น เอาแค่ plo)
        type_plo ใน ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เป็นเกณฑ์ภาษาอังกฤษที่มีลำดับ เช่น plo1 plo2 k2 s2 e1 c1 ต้องมีทั้งตัวอักษรและเลข) 
        detail_plo ใน ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เป็นเกณฑ์ภาษาอังกฤษที่มีลำดับ เช่น PLO 1 PLO 2 K2 S2 E1 C1 เอามาแค่คำอธิบายของเกณฑ์นั้น)
        """


	
    schema = {
    "type": "object",
    "properties": {
        "curr_philosophy": {"type": ["string", "null"]},
        "curr_objective": {"type": ["string", "null"]},
        "plo": {
            "type": ["array","null"],
            "items": {
                "type": "object",
                "properties": {
                    "type_plo": {"type": ["string", "null"]},
                    "detail_plo": {"type": ["string", "null"]},
                },
                "required": ["type_plo", "detail_plo"],
            },
        },
    },
    "additionalProperties": False,
    "required": []
    }


    return schema, prompt