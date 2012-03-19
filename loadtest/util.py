from dateutil.parser import parse as dateparse

def string_to_date(d, is_datetime):
    d = dateparse(d)
    if not is_datetime:
       return d.date()
    else:
        return d
