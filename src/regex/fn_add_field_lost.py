def add_field_lost(data1, master_schema):
    data = data1
    schema = master_schema

    def _types(sch):
        t = sch.get("type")
        if isinstance(t, list):
            return t
        if isinstance(t, str):
            return [t]
        return []

    def _default_for(sch):
        ts = _types(sch)

        # ตามที่คุณต้องการ (แต่ด้านล่างผมจะปรับ: object/array ที่ "จำเป็นต้องเป็น container" ให้เป็น {} / []
        # ในส่วนนี้ยังคงเดิมไว้ก่อน
        if "object" in ts or "array" in ts:
            return None
        if "string" in ts:
            return ""
        if "integer" in ts:
            return 0
        if "number" in ts:
            return 0
        if "boolean" in ts:
            return False
        return None

    def _clean_value_by_schema(v, v_schema):
        """ทำความสะอาดค่าตาม schema แบบ recursive"""
        ts = _types(v_schema)

        if v is None:
            return v

        if "object" in ts and isinstance(v, dict):
            _clean_object(v, v_schema)
            return v

        if "array" in ts and isinstance(v, list):
            items_schema = v_schema.get("items")
            if isinstance(items_schema, dict):
                item_types = _types(items_schema)
                if "object" in item_types:
                    for item in v:
                        if isinstance(item, dict):
                            _clean_object(item, items_schema)
                else:
                    # primitive list: ไม่บังคับแปลง type
                    pass
            return v

        return v  # primitive

    def _clean_object(obj, obj_schema):
        props = obj_schema.get("properties")
        addl = obj_schema.get("additionalProperties", None)

        # ---------
        # CASE A: object แบบปกติที่มี properties (และ additionalProperties=False) -> ลบ key เกินได้
        # ---------
        if isinstance(props, dict) and props:
            # 1) ลบ key ที่เกิน (เมื่อ additionalProperties=False เท่านั้น)
            if obj_schema.get("additionalProperties", True) is False:
                for k in list(obj.keys()):
                    if k not in props:
                        del obj[k]

            # 2) เติม/ทำความสะอาด key ที่ schema กำหนด
            for k, k_schema in props.items():
                if k not in obj or obj[k] is None:
                    obj[k] = _default_for(k_schema)
                    continue
                obj[k] = _clean_value_by_schema(obj[k], k_schema)
            return

        # ---------
        # CASE B: object แบบ "map" (ไม่มี properties แต่มี additionalProperties เป็น schema)
        # เช่น years: { "2569": 30, ... }
        # ---------
        if isinstance(addl, dict):
            # ห้ามลบ key เพราะ key เป็น dynamic
            # แค่ clean value ตาม schema ของ additionalProperties
            for k in list(obj.keys()):
                obj[k] = _clean_value_by_schema(obj[k], addl)
            return

        # ---------
        # CASE C: ไม่มี properties และไม่มี additionalProperties schema ชัด -> ไม่ทำอะไรกับ key
        # ---------
        return

    root_types = _types(schema)
    if "object" in root_types:
        if not isinstance(data, dict):
            data = {}
        _clean_object(data, schema)
        return data

    return _default_for(schema)
