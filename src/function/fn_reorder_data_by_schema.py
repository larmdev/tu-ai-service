def reorder_by_schema(data, schema):
    """
    เรียง key ตาม schema โดย:
    - object ที่มี properties -> เรียงตาม properties
    - object ที่ไม่มี properties แต่มี additionalProperties -> เก็บ key ทั้งหมดไว้ (เช่น years)
    - array -> recurse ตาม items
    - รองรับ type เป็น list เช่น ["object","null"]
    """

    if data is None or not isinstance(schema, dict):
        return data

    # ---- normalize schema type (รองรับ list เช่น ["object","null"]) ----
    t = schema.get("type")
    if isinstance(t, list):
        if "object" in t:
            schema_type = "object"
        elif "array" in t:
            schema_type = "array"
        elif len(t) > 0:
            schema_type = t[0]
        else:
            return data
    else:
        schema_type = t

    # ---- OBJECT ----
    if schema_type == "object" and isinstance(data, dict):
        props = schema.get("properties")
        addl = schema.get("additionalProperties", None)

        # 1) มี properties -> เรียงตาม properties
        if isinstance(props, dict) and len(props) > 0:
            ordered = {}

            # เรียงตาม schema.properties
            for key, sub_schema in props.items():
                if key in data:
                    ordered[key] = reorder_by_schema(data[key], sub_schema)

            # extra keys (ที่ schema ไม่กำหนด)
            extra_keys = [k for k in data.keys() if k not in props]

            # ถ้า additionalProperties เป็น dict -> recurse ด้วย schema นั้น
            if isinstance(addl, dict):
                for k in extra_keys:
                    ordered[k] = reorder_by_schema(data[k], addl)

            # ถ้า additionalProperties == False -> ทิ้ง extra
            elif addl is False:
                pass

            # ถ้า True หรือไม่กำหนด -> เก็บ extra ต่อท้าย
            else:
                for k in extra_keys:
                    ordered[k] = data[k]

            return ordered

        # 2) ไม่มี properties แต่มี additionalProperties (เช่น years)
        if isinstance(addl, dict):
            # เก็บทุก key และถ้าต้องการ recurse ตาม additionalProperties ก็ทำได้
            return {k: reorder_by_schema(v, addl) for k, v in data.items()}

        # 3) ไม่มี props และไม่มี additionalProperties -> คืนเดิม
        return dict(data)

    # ---- ARRAY ----
    if schema_type == "array" and isinstance(data, list):
        item_schema = schema.get("items", {})
        return [reorder_by_schema(item, item_schema) for item in data]

    # ---- PRIMITIVE ----
    return data
