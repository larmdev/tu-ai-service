from .fn_add_field_lost import add_field_lost
from regex.fn_clean_all import clean_all
def clean (master_schema,data1,data2,data3 ):

    for src in (data2, data3):
        if isinstance(src, dict):
            for k, v in src.items():
                if k not in data1 or data1[k] is None:
                    data1[k] = v

    # ----------------------------
    # 1) แปลง curriculumMapping.courses.plos
    #    - ใช้ head_plos เป็น key ทั้งหมด
    #    - ค่าเป็น True ถ้าเดิมมีอยู่ใน array plos, ไม่มีก็ False
    # ----------------------------
    head_plos = data1.get("head_plos") or []
    if not isinstance(head_plos, list):
        head_plos = []

    cm = data1.get("curriculumMapping")
    if isinstance(cm, list):
        for group in cm:
            if not isinstance(group, dict):
                continue
            courses = group.get("courses")
            if not isinstance(courses, list):
                continue

            for course in courses:
                if not isinstance(course, dict):
                    continue

                old_plos = course.get("plos") or []
                if not isinstance(old_plos, list):
                    old_plos = []

                old_set = set([p for p in old_plos if p is not None])

                new_plos = {}
                for p in head_plos:
                    if p is None:
                        continue
                    new_plos[str(p)] = (p in old_set)

                course["plos"] = new_plos

    # ลบ head_plos ออกให้เหมือน master_schema
    if "head_plos" in data1:
        del data1["head_plos"]

    # ----------------------------
    # 2) แปลง yearEndLearningOutcomeExpectations.expectations.plos
    #    - ใช้ head_plos_yearEndLearningOutcomeExpectations เป็น key ทั้งหมด
    #    - ค่าเป็น True ถ้าเดิมมีอยู่ใน array plos, ไม่มีก็ False
    # ----------------------------
    head_plos_yeloe = data1.get("head_plos_yearEndLearningOutcomeExpectations") or []
    if not isinstance(head_plos_yeloe, list):
        head_plos_yeloe = []

    yeloe = data1.get("yearEndLearningOutcomeExpectations")
    if isinstance(yeloe, list):
        for year_block in yeloe:
            if not isinstance(year_block, dict):
                continue

            expectations = year_block.get("expectations")
            if not isinstance(expectations, list):
                continue

            for exp in expectations:
                if not isinstance(exp, dict):
                    continue

                old_plos = exp.get("plos") or []
                if not isinstance(old_plos, list):
                    old_plos = []

                old_set = set([p for p in old_plos if p is not None])

                new_plos = {}
                for p in head_plos_yeloe:
                    if p is None:
                        continue
                    new_plos[str(p)] = (p in old_set)

                exp["plos"] = new_plos

    # ลบ head_plos_yearEndLearningOutcomeExpectations ออกให้เหมือน master_schema
    if "head_plos_yearEndLearningOutcomeExpectations" in data1:
        del data1["head_plos_yearEndLearningOutcomeExpectations"]

    data1 = add_field_lost(master_schema=master_schema,data1=data1)
    
    list_un_space = []
    data1 = clean_all(list_un_space=list_un_space,data1=data1)
    return data1