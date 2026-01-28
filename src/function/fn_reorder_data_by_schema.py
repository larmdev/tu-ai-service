def reorder_data_by_schema(data, schema):
    """
    ฟังก์ชันสำหรับเรียงลำดับ Key ใน Data ให้ตรงตามลำดับใน Schema
    รองรับทั้ง Object และ Array แบบ Nested (ซ้อนกัน)
    """
    
    # กรณีข้อมูลเป็น None หรือ Schema ไม่มี Type ให้คืนค่าเดิมกลับไป
    if data is None or 'type' not in schema:
        return data

    schema_type = schema['type']

    # 1. กรณีเป็น Object (Dictionary) -> เรียง Key ตาม properties
    if schema_type == 'object' and isinstance(data, dict):
        ordered_data = {}
        properties = schema.get('properties', {})
        
        # วนลูปตามลำดับ Key ใน Schema
        for key, sub_schema in properties.items():
            if key in data:
                # เรียกฟังก์ชันตัวเองซ้ำ (Recursion) เพื่อจัดการลูกหลานข้างใน
                ordered_data[key] = reorder_data_by_schema(data[key], sub_schema)
        
        # (Optional) ถ้ามี Key ใน Data ที่ไม่อยู่ใน Schema ให้ต่อท้ายไป (กันข้อมูลหาย)
        for key, value in data.items():
            if key not in properties:
                ordered_data[key] = value
                
        return ordered_data

    # 2. กรณีเป็น Array (List) -> วนลูปจัดการ items ข้างใน
    elif schema_type == 'array' and isinstance(data, list):
        item_schema = schema.get('items', {})
        return [reorder_data_by_schema(item, item_schema) for item in data]

    # 3. กรณีเป็นค่าธรรมดา (String, Int, Boolean) -> คืนค่าเดิม
    else:
        return data