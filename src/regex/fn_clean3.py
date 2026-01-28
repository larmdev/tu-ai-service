from fn_add_field_lost import add_field_lost
from fn_clean import clean
def clean (master_schema,data1 ):

    data1 = add_field_lost(master_schema=master_schema,data1=data1)
    
    list_un_space = []
    data1 = clean(list_un_space=list_un_space,data1=data1)
    return data1