from .fn_add_field_lost import add_field_lost
from regex.fn_clean_all import clean_all
def clean (master_schema,data1 ):

    print("before",data1)
    students_per_year = data1.get("studentsPerYear")

    plans = data1.get("studentAdmissionPlans")
    if isinstance(plans, list):
        for plan in plans:
            if not isinstance(plan, dict):
                continue

            head_years = plan.get("head_studentAdmissionPlans") or []
            if not isinstance(head_years, list):
                head_years = []

            rows = plan.get("rows")
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue

                    old_years = row.get("years") or []
                    year_map = {}
                    if isinstance(old_years, list):
                        for y in old_years:
                            if isinstance(y, dict):
                                be = y.get("BEyear")
                                detail = y.get("detail_year")
                                if be is not None:
                                    year_map[be] = detail

                    new_years = {}
                    for be in head_years:
                        key = str(be)
                        if be in year_map and year_map[be] is not None:
                            new_years[key] = year_map[be]
                        else:
                            new_years[key] = students_per_year

                    row["years"] = new_years

            if "head_studentAdmissionPlans" in plan:
                del plan["head_studentAdmissionPlans"]

    data1 = add_field_lost(master_schema=master_schema,data1=data1)
    
    list_un_space = []
    data1 = clean_all(list_un_space=list_un_space,data1=data1)
    return data1