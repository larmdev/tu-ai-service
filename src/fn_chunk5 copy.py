
def schema_prompt(chunk_pdf_bytes: bytes=None):


    prompt = """จากในไฟล์ที่ทำการ extract เรียงจากบนลงล่าง ห้ามตอบคำอธิบายอื่น ให้ตอบเป็น JSON อย่างเดียว ตาม schema ที่กำหนด
    หมวดที่ 5

    (หมวดนี้อยู่ใน การพัฒบุคคลตามวิชาชีพหรือศาสตร์ มีหัวตารางคือ คุณลักษณะของนักศึกษา และ ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) โดยคำว่าคุณลักษณะบุคคลทั่วไป และ คุณลักษณะบุคคลตามวิชาชีพหรือศาสตร์ คุณลักษณะของนักศึกษา การพัฒนาหลักสูตร พร้อมข้อความอื่นๆ โดยบางทีตารางก็ออกมาในรุปแบบ 2*2 บางอันแบ่ง row ของแต่ละ คุณลักษณะของนักศึกษา รวมถึงวิธีการดําเนินการ ด้วย บางทีตารางอาจถูกตัดจากหน้าที่เปลี่ยนไปให้เช็คด้วย)
    general_character คุณลักษณะของนักศึกษา ของ คุณลักษณะบุคคลทั่วไป (หากมีหลายข้อ ไม่ต้องเอาละดับมาเอามาแค่ข้อ และใส่ ',' คั่น)
    plo_general_character ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) ของ คุณลักษณะบุคคลทั่วไป (หากมีหลายข้อ ไม่ต้องเอาละดับมาเอามาแค่ข้อ และใส่ ',' คั่น  และไม่เอาตัวที่ซ้ำ)
    profession_character คุณลักษณะของนักศึกษา ของ คุณลักษณะบุคคลตามวิชาชีพหรือศาสตร์ (หากมีหลายข้อ ไม่ต้องเอาละดับมาเอามาแค่ข้อ และใส่ ',' คั่น)
    plo_profession_character ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) ของ คุณลักษณะบุคคลตามวิชาชีพหรือศาสตร์ (หากมีหลายข้อ ไม่ต้องเอาละดับมาเอามาแค่ข้อ และใส่ ',' คั่น และไม่เอาตัวที่ซ้ำ)

    (หมวดนี้อยู่ใน ตารางแสดงความสัมพันธ์ระหว่างผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) กับมาตรฐานคุณวุฒิระดับอุดมศึกษา)
    plo_quality_qualification (เป็นตาราง โดยมีหัวตารางหลักคือ ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) ,ประเภท ซึ่งมีสองหัวย่อยคือ ทั่วไป(Generic) กับ เฉพาะ(Specific) ,Bloom’s Taxonomy ซึ่งมีสองหัวย่อยคือ Domain กับ Level และสุดท้ายคือ รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา ซึ่งมีหลายค่า บางทีตารางอาจถูกตัดจากหน้าที่เปลี่ยนไปให้เช็คด้วย)
    header_plo_quality_qualification เป็นหัวตารางย่อยของ รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา
    detail_plo_quality_qualification (รายละเอียดของแต่ละแถว)
        general_or_specific (เก็บค่าตารางของหัวข้อ ประเภท)
        general ค่าจาก general (หากถูกติ้กหรือมีค่า ให้ใช้ค่า 1 หากไม่ให้ใช้ 0)
        specific ค่าจาก specific (หากถูกติ้กหรือมีค่า ให้ใช้ค่า 1 หากไม่ให้ใช้ 0)
        bloom_taxonomy (เก็บค่าตารางของหัวข้อ ประเภท)
        domain ค่าจาก domain (เอาข้อความมาทั้งหมด)
        level ค่าจาก level (เอาข้อความมาทั้งหมด)
        detail_plo_qualification ค่าจากแต่ละหัวข้อของ รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา (จำนวนแต่ละแถวต้องมีค่าเท่ากับ จำนวนหัวข้อย่อยของ รายละเอียดผลลัพธ์การเรียนรู้ตามมาตรฐานคุณวุฒิระดับอุดมศึกษา และ หากถูกติ้กหรือมีค่า ให้ใช้ค่า 1 หากไม่ให้ใช้ 0)

    (อยู่ในหมวด ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) กลยุทธ์/วิธีการสอน และ กลยุทธ์/วิธีการวัดและการประเมินผล บางทีตารางอาจถูกตัดจากหน้าที่เปลี่ยนไปให้เช็คด้วย)
    plo_evaluate (เป็นตารางซึ่งมีหัวตาราง ผลลัพธ์การเรียนรู้ระดับหลักสูตร กลยุทธ์/วิธีการสอน วิธีการวัดและประเมินผล บางทีอาจมี ลำดับ ด้วย)
        plo_curr_level ผลลัพธ์การเรียนรู้ระดับหลักสูตร (เอาข้อความมาทั้งหมด หากมี ลำดับ ให้เอาข้อความจากลำดับมาเป็นคำตั้งต้นของ ตัวแปรนี้)
        plo_strategy กลยุทธ์/วิธีการสอน (เอาข้อความทั้งหมด หากมีหลายข้อ ไม่ต้องเอาลำดับ โดยให้คั่นด้วย ',')
        plo_measure_evaluate วิธีการวัดและประเมินผล (เอาข้อความทั้งหมด หากมีหลายข้อ ไม่ต้องเอาลำดับ โดยให้คั่นด้วย ',')

    (หมวดนี้อยู่ใน แผนที่แสดงการกระจายความรับผิดชอบผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) สู่รายวิชา (Curriculum Mapping))
    plo_curriculum_mapping (เป็นตาราง โดยมีหัวตารางหลักคือ รายวิชา / ชุดวิชา และ หน่วยกิต ,หน่วยกิต ,ชั้นปีที่ และสุดท้ายคือ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) ซึ่งมีหลายค่า บางทีตารางอาจถูกตัดจากหน้าที่เปลี่ยนไปให้เช็คด้วย)
    header_plo_curriculum_mapping เป็นหัวตารางย่อยของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)
    detail_plo_curriculum_mapping (รายละเอียดของตาราง)
        type_plo_mapping ประเภท/หมวด (เป็นข้อความที่ทั้งแถวมีค่าเดียว เป็นข้อความ เอาข้อความมาทั้งหมด อาจเจอคำเช่น หมวดวิชาศึกษาทั่วไป หมวดวิชาเฉพาะ)
        detail_plo_mapping (รายละเอียดแต่ละแถว)
        course รายวิชา / ชุดวิชา และ หน่วยกิต
        credit หน่วยกิต
        year ชั้นปีที่
        detail_plo ค่าจากแต่ละหัวข้อของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) (จำนวนแต่ละแถวต้องมีค่าเท่ากับ จำนวนหัวข้อย่อยของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) และ หากถูกติ้กหรือมีค่า ให้ใช้ค่า 1 หากไม่ให้ใช้ 0)

    (อยู่ในหมวด ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา)
    plo_expectation (เป็นตาราง โดยมีหัวตารางหลักคือ ชั้นปี ,ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา ,ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs) ซึ่งมีหลายค่า บางทีตารางอาจถูกตัดจากหน้าที่เปลี่ยนไปให้เช็คด้วย)
    header_plo_expectation เป็นหัวตารางย่อยของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)
    detail_table_plo_expectation (รายละเอียดทั้งหมดของตาราง)
        year_plo_expectation ชั้นปี
        detail_plo_expectation (รายละเอียดของแต่ละชั้นปี)
        expectation_end_year ความคาดหวังของผลลัพธ์การเรียนรู้เมื่อสิ้นปีการศึกษา (เอาข้อความมาแต่ไม่ต้องเอาลำดับมา)
        each_plo_expectation ค่าจากแต่ละหัวข้อของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) (จำนวนแต่ละแถวต้องมีค่าเท่ากับ จำนวนหัวข้อย่อยของ ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs) และ หากถูกติ้กหรือมีค่า ให้ใช้ค่า 1 หากไม่ให้ใช้ 0)

    (องค์ประกอบเกี่ยวกับประสบการณ์ภาคสนาม (การฝึกงาน หรือสหกิจศึกษา))
    practical_period ช่วงเวลา (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',' หากเป็นตารางที่มีหัวข้อ ชั้นปี ภาคการศึกษา รายวิชา ให้เอาแต่ละแถวมาเป็นหัวข้อ และในทุกค่า ก็ใส่หัวข้อรายละเอียดค่ามา)
    practical_prepare การเตรียมการ (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',' และถ้าหากหัวข้อนั้นมีหัวข้อย่อย ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',')
    practical_evaluate การประเมินผล (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',' และถ้าหากหัวข้อนั้นมีหัวข้อย่อย ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',')

    (ข้อกําหนดเกี่ยวกับการทําโครงงาน หรือ งานวิจัย)
    research_period ช่วงเวลา (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',')
    research_prepare การเตรียมการ (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',')
    research_evaluate การประเมินผล (เอาข้อความทั้งหมด หากมีหัวข้อต่างๆๆ ดูได้จากเลขให้เอาแต่ละข้อใส่ในวงเล็บ '{}' และคั่นด้วย ',')
    """

    # มีตัวแปรซ้ำ: credit (ซ้ำหลายชั้น), year (ซ้ำหลายชั้น), plo_expectation (ซ้ำเป็นชื่อฟิลด์หลักและชื่อฟิลด์ย่อย), detail_plo (ซ้ำหลายชั้น)

    schema = {
        "type": "object",
        "properties": {
            "general_character": {"type": ["string", "null"]},
            "plo_general_character": {"type": ["string", "null"]},
            "profession_character": {"type": ["string", "null"]},
            "plo_profession_character": {"type": ["string", "null"]},

            "plo_quality_qualification": {
                "type": ["object", "null"],
                "properties": {
                    "header_plo_quality_qualification": {
                        "type": ["array", "null"],
                        "items": {"type": ["string", "null"]},
                    },
                    "detail_plo_quality_qualification": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "general_or_specific": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "general": {"type": ["string", "null"]},
                                        "specific": {"type": ["string", "null"]},
                                    },
                                    "required": [],
                                    "additionalProperties": False,
                                },
                                "bloom_taxonomy": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "domain": {"type": ["string", "null"]},
                                        "level": {"type": ["string", "null"]},
                                    },
                                    "required": [],
                                    "additionalProperties": False,
                                },
                                "detail_plo_qualification": {
                                    "type": ["array", "null"],
                                    "items": {"type": ["integer", "null"]},
                                },
                            },
                            "required": [],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["header_plo_quality_qualification","detail_plo_quality_qualification"],
                "additionalProperties": False,
            },

            "plo_evaluate": {
                "type": ["array", "null"],
                "items": {
                    "type": "object",
                    "properties": {
                        "plo_curr_level": {"type": ["string", "null"]},
                        "plo_strategy": {"type": ["string", "null"]},
                        "plo_measure_evaluate": {"type": ["string", "null"]},
                    },
                    "required": ["plo_curr_level","plo_strategy","plo_measure_evaluate"],
                    "additionalProperties": False,
                },
            },

            "plo_curriculum_mapping": {
                "type": ["object", "null"],
                "properties": {
                    "header_plo_curriculum_mapping": {
                        "type": ["array", "null"],
                        "items": {"type": ["string", "null"]},
                    },
                    "detail_plo_curriculum_mapping": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "type_plo_mapping": {"type": ["string", "null"]},
                                "detail_plo_mapping": {
                                    "type": ["object", "null"],
                                    "properties": {
                                        "course": {"type": ["string", "null"]},
                                        "credit": {"type": ["string", "null"]},
                                        "year": {"type": ["string", "null"]},
                                        "detail_plo": {
                                            "type": ["array", "null"],
                                            "items": {"type": ["integer", "null"]},
                                        },
                                    },
                                    "required": [],
                                    "additionalProperties": False,
                                },
                            },
                            "required": ["type_plo_mapping","detail_plo_mapping"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["header_plo_curriculum_mapping","detail_plo_curriculum_mapping"],
                "additionalProperties": False,
            },

            "plo_expectation": {
                "type": ["object", "null"],
                "properties": {
                    "header_plo_expectation": {
                        "type": ["array", "null"],
                        "items": {"type": ["string", "null"]},
                    },
                    "detail_table_plo_expectation": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "year_plo_expectation": {"type": ["string", "null"]},
                                "detail_plo_expectation": {
                                    "type": ["array", "null"],
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "expectation_end_year": {"type": ["string", "null"]},
                                            "each_plo_expectation": {
                                                "type": ["array", "null"],
                                                "items": {"type": ["integer", "null"]},
                                            },
                                        },
                                        "required": ["each_plo_expectation"],
                                        "additionalProperties": False,
                                    },
                                },
                            },
                            "required": ["year_plo_expectation","detail_plo_expectation"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["header_plo_expectation","detail_table_plo_expectation"],
                "additionalProperties": False,
            },

            "practical_period": {"type": ["string", "null"]},
            "practical_prepare": {"type": ["string", "null"]},
            "practical_evaluate": {"type": ["string", "null"]},
            "research_period": {"type": ["string", "null"]},
            "research_prepare": {"type": ["string", "null"]},
            "research_evaluate": {"type": ["string", "null"]},
        },
        "required": [],
        "additionalProperties": False,
    }


    return schema, prompt