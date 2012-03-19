import random
from propertygenerartors import _rand_chars, ALPHA, NUMBERS, _rand_date
from datetime import date, datetime, timedelta

def get_property_name(index):
    return "PROPERTY_%s" % str(index)

def get_text_options():
    return ['text', random.randint(1,15), random.choice([True,False])]

def get_alphanumeric_options():
    return ['alphanumeric', random.randint(1,15), random.choice([True,False])]

def get_number_options():
    return ['number', random.randint(1,15), random.choice([True,False])]

def get_double_options():
    return ['double']

def _make_select_list(type):
    ret = []
    for i in range(random.randint(1,8)):
        ret.append(_rand_chars(ALPHA,random.randint(1,15)))
    return [type] + ret


def get_select_options():
    return _make_select_list('select')

def get_select1_options():
    return _make_select_list('select1')

def _make_date_option(type):
    td = timedelta(days=(365*3)) #3 years ago from today
    t1 = None
    t2 = None
    if type == 'date':
        t2 = date.today()
    else:
        t2 = datetime.now()

    t1 = t2 - td
    return [type,str(t1),str(t2)]

def get_date_options():
    return _make_date_option('date')

def get_datetime_options():
    return _make_date_option('datetime')

def pick_random_func():
    func_list = [
        get_text_options,
        get_number_options,
        get_double_options,
        get_select_options,
        get_select1_options,
        get_date_options,
        get_datetime_options,
        get_alphanumeric_options
    ]
    return random.choice(func_list)

def getspec(num_props):
    """
    Only for explicit=False!
    """
    spec = {"explicit": False}
    case = {}
    for i in range(num_props):
        case[get_property_name(i)] = pick_random_func()()

    spec["case"] = case
    return spec