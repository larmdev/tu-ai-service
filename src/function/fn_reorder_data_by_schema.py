def reorder_by_schema(data, schema, no_deep_keys=None):
    if no_deep_keys is None:
        no_deep_keys = set()
    else:
        no_deep_keys = set(no_deep_keys)

    if data is None or not isinstance(schema, dict):
        return data

    sch_type = schema.get("type")
    if isinstance(sch_type, list):
        if "object" in sch_type:
            sch_type = "object"
        elif "array" in sch_type:
            sch_type = "array"
        else:
            sch_type = sch_type[0] if sch_type else None

    # ---------- OBJECT ----------
    if sch_type == "object" and isinstance(data, dict):
        props = schema.get("properties")
        addl = schema.get("additionalProperties", None)

        # 1) ถ้ามี properties -> เรียงตาม properties ก่อน
        if isinstance(props, dict) and props:
            ordered = {}
            for key, sub_schema in props.items():
                if key not in data:
                    continue

                # ✅ ยกทั้งก้อนถ้าอยู่ใน no_deep_keys
                if key in no_deep_keys:
                    ordered[key] = data[key]
                else:
                    ordered[key] = reorder_by_schema(data[key], sub_schema, no_deep_keys)

            # 2) key ที่ไม่อยู่ใน properties
            extra_keys = [k for k in data.keys() if k not in props]

            # additionalProperties เป็น dict -> recurse ต่อ
            if isinstance(addl, dict):
                for k in extra_keys:
                    ordered[k] = reorder_by_schema(data[k], addl, no_deep_keys)
            # additionalProperties True/None -> เก็บต่อท้าย
            elif addl is True or addl is None:
                for k in extra_keys:
                    ordered[k] = data[k]
            # additionalProperties False -> ทิ้ง extra

            return ordered

        # 2) ถ้าไม่มี properties (เช่น years) แต่มี additionalProperties -> ต้องคง key ทั้งหมดไว้
        if isinstance(addl, dict):
            # recurse ตาม schema ของ additionalProperties (เช่น integer/null)
            return {k: reorder_by_schema(v, addl, no_deep_keys) for k, v in data.items()}

        # 3) ไม่มีทั้ง properties และ additionalProperties เป็น dict -> คืน data เดิม
        return dict(data)

    # ---------- ARRAY ----------
    if sch_type == "array" and isinstance(data, list):
        item_schema = schema.get("items", {})
        return [reorder_by_schema(item, item_schema, no_deep_keys) for item in data]

    # ---------- PRIMITIVE ----------
    return data
