def add_field_lost(data1, master_schema):
    data = data1
    schema = master_schema

    list_not_change = {"ApprovedByUniversityCouncilMeetingNumber","ApprovedByUniversityCouncilDate","ApprovedByProfessionalCouncilMeetingNumber","ApprovedByProfessionalCouncilDate","ApprovedByPolicyCommitteeMeetingNumber", "ApprovedByPolicyCommitteeDate",}   # ตัวอย่าง: b,c เป็น null แล้วปล่อยไว้

    def _types(sch):
        t = sch.get("type")
        if isinstance(t, list):
            return t
        if isinstance(t, str):
            return [t]
        return []

    def _default_for(sch):
        ts = _types(sch)
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

    def _clean_value_by_schema(v, v_schema, *, in_list_item=False):
        ts = _types(v_schema)

        # ถ้าอยู่ใน list item แล้วเป็น None -> ปล่อย None
        if v is None and in_list_item:
            return None

        # กรณีอื่น ๆ เป็น None -> เติม default
        if v is None:
            return _default_for(v_schema)

        if "object" in ts and isinstance(v, dict):
            _clean_object(v, v_schema)
            return v

        if "array" in ts and isinstance(v, list):
            items_schema = v_schema.get("items")
            if isinstance(items_schema, dict):
                for i in range(len(v)):
                    v[i] = _clean_value_by_schema(v[i], items_schema, in_list_item=True)
            return v

        return v

    def _clean_object(obj, obj_schema):
        props = obj_schema.get("properties")
        addl = obj_schema.get("additionalProperties", None)

        if isinstance(props, dict) and props:
            if obj_schema.get("additionalProperties", True) is False:
                for k in list(obj.keys()):
                    if k not in props:
                        del obj[k]

            for k, k_schema in props.items():
                if k not in obj:
                    obj[k] = _default_for(k_schema)
                    continue

                # ✅ key มีอยู่ แต่เป็น null/None
                if obj[k] is None:
                    if k in list_not_change:
                        obj[k] = None                 # ไม่เติม default เฉพาะที่กำหนด
                    else:
                        obj[k] = _default_for(k_schema)  # ที่เหลือเติม default
                    continue

                obj[k] = _clean_value_by_schema(obj[k], k_schema, in_list_item=False)
            return

        if isinstance(addl, dict):
            for k in list(obj.keys()):
                obj[k] = _clean_value_by_schema(obj[k], addl, in_list_item=False)
            return

    root_types = _types(schema)
    if "object" in root_types:
        if not isinstance(data, dict):
            data = {}
        _clean_object(data, schema)
        return data

    return _default_for(schema)