import re
import unicodedata

from .fn_add_field_lost import add_field_lost
from regex.fn_clean_all import clean_all


def clean(master_schema, data1, data2, data3):

    # -----------------------------
    # Helpers (เป็นตัวแปร/ฟังก์ชันเล็ก ๆ ในสคริปต์เดียว)
    # -----------------------------

    def strip_dot_space(s: str) -> str:
        return re.sub(r"[.\s]+", "", s)

    def strip_space_only(s: str) -> str:
        return re.sub(r"\s+", "", s)

    def normalize_en_for_match(s: str) -> str:
        # uppercase + remove spaces
        return re.sub(r"\s+", "", (s or "").upper())

    def normalize_th_for_match(s: str) -> str:
        """
        ลบสระ/วรรณยุกต์/เครื่องหมายกำกับเสียง + space
        วิธี: NFD แล้วทิ้ง combining marks (Mn)
        """
        s = s or ""
        s = re.sub(r"\s+", "", s)
        s = unicodedata.normalize("NFD", s)
        s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
        return s

    def fill_nulls(dst: dict, src: dict):
        """ถ้า dst[k] เป็น None หรือไม่มี ให้เอาจาก src[k] (เฉพาะ key ที่ src มีและไม่ None)"""
        if not isinstance(dst, dict) or not isinstance(src, dict):
            return
        for k, v in src.items():
            if v is None:
                continue
            if k not in dst or dst[k] is None:
                dst[k] = v

    for src in (data2, data3):
        if isinstance(src, dict):
            for k, v in src.items():
                if k not in data1 or data1[k] is None:
                    data1[k] = v

    flat2 = []  # จาก schema2.courses -> detail_course
    c2 = data2.get("courses")
    if isinstance(c2, list):
        for g in c2:
            if not isinstance(g, dict):
                continue
            group_name = g.get("courseGroup")
            details = g.get("detail_course")
            if not isinstance(details, list):
                continue
            for d in details:
                if not isinstance(d, dict):
                    continue
                row = dict(d)
                row["courseGroup"] = group_name
                # sequence ไม่สนใจ
                row["sequence"] = None

                # clean code in data (in-place ใน row; และถ้าคุณต้องการแก้ใน data2 ด้วยจริง ๆ ต้องไล่แก้ต้นฉบับ แต่คุณบอก "แก้ใน data เลย"
                # ดังนั้นเราจะ clean แล้วเขียนกลับลง d ด้วย
                if isinstance(d.get("courseCodeTh"), str):
                    d["courseCodeTh"] = strip_space_only(d["courseCodeTh"])
                    row["courseCodeTh"] = d["courseCodeTh"]
                if isinstance(d.get("courseCodeEn"), str):
                    d["courseCodeEn"] = strip_dot_space(d["courseCodeEn"]).upper()
                    row["courseCodeEn"] = d["courseCodeEn"]

                flat2.append(row)

    flat3 = []  # จาก schema3.courses -> detail
    c3 = data3.get("courses")
    if isinstance(c3, list):
        for g in c3:
            if not isinstance(g, dict):
                continue
            group_name = g.get("courseGroup")
            details = g.get("detail")
            if not isinstance(details, list):
                continue
            for d in details:
                if not isinstance(d, dict):
                    continue
                row = dict(d)
                row["courseGroup"] = group_name
                row["sequence"] = None

                # clean code in data3 ด้วย
                if isinstance(d.get("courseCodeTh"), str):
                    d["courseCodeTh"] = strip_space_only(d["courseCodeTh"])
                    row["courseCodeTh"] = d["courseCodeTh"]
                if isinstance(d.get("courseCodeEn"), str):
                    d["courseCodeEn"] = strip_dot_space(d["courseCodeEn"]).upper()
                    row["courseCodeEn"] = d["courseCodeEn"]

                flat3.append(row)

    idx2_code_th = {}
    idx2_code_en = {}
    idx2_name_th = {}
    idx2_name_en = {}

    for i, c in enumerate(flat2):
        ct = c.get("courseCodeTh")
        ce = c.get("courseCodeEn")
        nt = c.get("courseNameTh")
        ne = c.get("courseNameEn")

        if isinstance(ct, str) and ct:
            idx2_code_th[ct] = i
        if isinstance(ce, str) and ce:
            idx2_code_en[ce] = i
        if isinstance(nt, str) and nt:
            idx2_name_th[normalize_th_for_match(nt)] = i
        if isinstance(ne, str) and ne:
            idx2_name_en[normalize_en_for_match(ne)] = i

    def find_match_in_flat2(c):
        ct = c.get("courseCodeTh")
        if isinstance(ct, str) and ct and ct in idx2_code_th:
            return idx2_code_th[ct]

        ce = c.get("courseCodeEn")
        if isinstance(ce, str) and ce and ce in idx2_code_en:
            return idx2_code_en[ce]

        nt = c.get("courseNameTh")
        if isinstance(nt, str) and nt:
            key = normalize_th_for_match(nt)
            if key in idx2_name_th:
                return idx2_name_th[key]

        ne = c.get("courseNameEn")
        if isinstance(ne, str) and ne:
            key = normalize_en_for_match(ne)
            if key in idx2_name_en:
                return idx2_name_en[key]

        return None

    # merge: เอา flat3 ไปเติม flat2 (fill nulls)
    for c in flat3:
        j = find_match_in_flat2(c)
        if j is not None:
            # เติม nulls ใน flat2[j] ด้วยค่าจาก c
            fill_nulls(flat2[j], c)
            # ถ้า courseGroup ใน flat2 ไม่มี แต่ c มี -> เติม
            if (flat2[j].get("courseGroup") is None) and (
                c.get("courseGroup") is not None
            ):
                flat2[j]["courseGroup"] = c.get("courseGroup")
        else:
            # ไม่เจอใน flat2 -> add เข้า all_course
            flat2.append(c)
            # และ update index ให้ match ตัวต่อไปได้
            i = len(flat2) - 1
            ct = c.get("courseCodeTh")
            ce = c.get("courseCodeEn")
            nt = c.get("courseNameTh")
            ne = c.get("courseNameEn")
            if isinstance(ct, str) and ct:
                idx2_code_th[ct] = i
            if isinstance(ce, str) and ce:
                idx2_code_en[ce] = i
            if isinstance(nt, str) and nt:
                idx2_name_th[normalize_th_for_match(nt)] = i
            if isinstance(ne, str) and ne:
                idx2_name_en[normalize_en_for_match(ne)] = i

    all_course = flat2  # ตามที่คุณเรียก

    structure = data2.get("structure")
    master_courses = []
    used_all_course_idx = set()

    def match_all_course_to_courseTh(course_th: str):
        """
        คืน index ของ all_course ที่ match กับ courseTh
        เงื่อนไข:
        1) courseCodeTh (all_course) อยู่ใน courseTh (structure) หลัง normalize ไทย
        2) courseNameTh (all_course) อยู่ใน courseTh หลัง normalize ไทย
        """
        if not isinstance(course_th, str) or not course_th:
            return None

        target = normalize_th_for_match(course_th)

        # 1) code_th in courseTh
        for i, c in enumerate(all_course):
            code_th = c.get("courseCodeTh")
            if isinstance(code_th, str) and code_th:
                # normalize แบบไทยให้เทียบได้ (code_th ปกติเป็น latin/ตัวเลข ก็ไม่เสียหาย)
                if (
                    normalize_th_for_match(code_th)
                    and normalize_th_for_match(code_th) in target
                ):
                    return i

        # 2) name_th in courseTh
        for i, c in enumerate(all_course):
            name_th = c.get("courseNameTh")
            if isinstance(name_th, str) and name_th:
                key = normalize_th_for_match(name_th)
                if key and key in target:
                    return i

        return None

    if isinstance(structure, list):
        for block in structure:
            if not isinstance(block, dict):
                continue
            academic_year = block.get("academicYear")
            semester = block.get("semester")
            details = block.get("detail")
            if not isinstance(details, list):
                continue

            for d in details:
                if not isinstance(d, dict):
                    continue

                course_th = d.get("courseTh")
                credits = d.get("credits")
                lpss = d.get("lecturePracticeSelfStudy")

                # โครง master ต่อ 1 วิชา
                row = {
                    "sequence": None,  # ตามที่คุณต้องการ
                    "courseCodeTh": None,
                    "courseCodeEn": None,
                    "courseNameTh": None,
                    "courseNameEn": None,
                    "courseDescriptionTh": None,
                    "courseDescriptionEn": None,
                    "credits": credits,
                    "lecturePracticeSelfStudy": lpss,
                    "courseGroup": None,
                    "semester": semester,
                    "academicYear": academic_year,
                }

                mi = (
                    match_all_course_to_courseTh(course_th)
                    if isinstance(course_th, str)
                    else None
                )
                if mi is not None:
                    c = all_course[mi]
                    used_all_course_idx.add(mi)

                    # ใช้ข้อมูลจาก all_course เติม (และ fill null จาก structure ได้ด้วยบางส่วน)
                    row["courseGroup"] = c.get("courseGroup")
                    row["courseCodeTh"] = c.get("courseCodeTh")
                    row["courseCodeEn"] = c.get("courseCodeEn")
                    row["courseNameTh"] = c.get("courseNameTh") or course_th
                    row["courseNameEn"] = c.get("courseNameEn")
                    row["courseDescriptionTh"] = c.get("courseDescriptionTh")
                    row["courseDescriptionEn"] = c.get("courseDescriptionEn")

                    # ถ้ายัง null แต่ structure มี credits/lpss อยู่แล้ว row ใส่ไปแล้ว
                    # ถ้า structure ไม่มี แต่ all_course มี -> เติม
                    if row["credits"] is None and c.get("credits") is not None:
                        row["credits"] = c.get("credits")
                    if (
                        row["lecturePracticeSelfStudy"] is None
                        and c.get("lecturePracticeSelfStudy") is not None
                    ):
                        row["lecturePracticeSelfStudy"] = c.get(
                            "lecturePracticeSelfStudy"
                        )
                else:
                    # unmapped จาก all_course -> ใช้ fallback ตามที่คุณบอก
                    row["courseNameTh"] = course_th
                    # อื่น ๆ ให้คง None (หรือจะใส่ courseTh ไปลง En/Description ตามที่คุณต้องการก็ได้)
                    # คุณพิมพ์ว่า: "courseGroup" "courseNameTh" "courseCodeEn" "courseNameEn": "courseDescriptionEn"
                    # ประโยคนี้ตีความได้หลายแบบ ผมตีความแบบปลอดภัย: ใส่ courseNameTh = courseTh และที่เหลือ None
                    # ถ้าคุณอยากให้ courseDescriptionEn = courseTh ด้วย ให้เปิดบรรทัดด้านล่าง:
                    # row["courseDescriptionEn"] = course_th

                master_courses.append(row)

    APPEND_UNMAPPED_ALL_COURSE = True  # เปลี่ยนเป็น True ถ้าต้องการ

    if APPEND_UNMAPPED_ALL_COURSE:
        for i, c in enumerate(all_course):
            if i in used_all_course_idx:
                continue
            master_courses.append(
                {
                    "sequence": None,
                    "courseCodeTh": c.get("courseCodeTh"),
                    "courseCodeEn": c.get("courseCodeEn"),
                    "courseNameTh": c.get("courseNameTh"),
                    "courseNameEn": c.get("courseNameEn"),
                    "courseDescriptionTh": c.get("courseDescriptionTh"),
                    "courseDescriptionEn": c.get("courseDescriptionEn"),
                    "credits": c.get("credits"),
                    "lecturePracticeSelfStudy": c.get("lecturePracticeSelfStudy"),
                    "courseGroup": c.get("courseGroup"),
                    "semester": None,
                    "academicYear": None,
                }
            )

    data1["courses"] = master_courses

    # academicRequirements: ตั้ง sequence เป็น None ตามที่คุณต้องการ
    ar = data1.get("academicRequirements")
    if isinstance(ar, list):
        for item in ar:
            if isinstance(item, dict):
                item["sequence"] = None

    # ลบ structure ออกให้ตรง master_schema
    if "structure" in data1:
        del data1["structure"]

    data1 = add_field_lost(master_schema=master_schema, data1=data1)

    list_un_space = []
    data1 = clean_all(list_un_space=list_un_space, data1=data1)
    return data1
