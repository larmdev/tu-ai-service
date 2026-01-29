def clean_all(list_un_space: list, data1):
    """
    1) Replace ในทุก string: " า" -> "ำ"
    2) ถ้ามี key ชื่อ "sequence" อยู่ใน dict ที่อยู่ใน list -> set sequence = index+1
    3) Remove '\n' (และ '\r') ในทุก string ยกเว้น field ที่ชื่ออยู่ใน list_un_space
    """

    keep_newline_fields = set(list_un_space or [])

    def fix_string(s: str, field_name: str | None):
        if not isinstance(s, str):
            return s

        # 1) replace " า" -> "ำ"
        s = s.replace(" า", "ำ")

        # 3) remove newline ยกเว้น field ที่อยู่ใน list_un_space
        # if field_name not in keep_newline_fields:
        #     s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "")

        return s

    def walk(value, field_name=None):
        # dict
        if isinstance(value, dict):
            for k in list(value.keys()):
                v = value[k]
                if isinstance(v, str):
                    value[k] = fix_string(v, k)
                else:
                    value[k] = walk(v, k)
            return value

        # list
        if isinstance(value, list):
            # 2) ถ้าใน list นี้มี dict ที่มี "sequence" -> รีเซ็ตทั้ง list
            has_sequence = any(isinstance(item, dict) and "sequence" in item for item in value)
            if has_sequence:
                seq = 1
                for item in value:
                    if isinstance(item, dict) and "sequence" in item:
                        item["sequence"] = seq
                        seq += 1

            # recurse members
            for i in range(len(value)):
                item = value[i]
                if isinstance(item, str):
                    value[i] = fix_string(item, None)
                else:
                    value[i] = walk(item, None)
            return value

        # primitive อื่นๆ
        return value

    walk(data1, None)
    return data1
