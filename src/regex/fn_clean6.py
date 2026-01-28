from fn_add_field_lost import add_field_lost
from fn_clean import clean_all
def clean (master_schema,data1,data2 ):
    print("data1->",data1)
    print("data2->",data2)
    for k, v in data2.items():
        if k not in data1 or data1[k] is None:
            data1[k] = v

    print("data1->",data1)

    data1 = add_field_lost(master_schema=master_schema,data1=data1)
    
    list_un_space = []
    data1 = clean_all(list_un_space=list_un_space,data1=data1)
    return data1