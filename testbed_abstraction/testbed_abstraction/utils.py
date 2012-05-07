import json
import pytz
import uuid
from datetime import datetime
from testbed_abstraction import config

# serialization of python dictionaries and lists into JSON format
# more info at http://docs.python.org/library/json.html

def serialize(dict_or_list):
    return json.dumps(dict_or_list, ensure_ascii = config.JSON_ENSURE_ASCII, indent = config.JSON_INDENT) + '\n'
    
# generated random 16 characters strings as identifiers
# more info at http://docs.python.org/library/uuid.html
    
def generate_id():
    return uuid.uuid4().hex

# datetime and time zone utility functions
# developer must set the local time zone first via the 'tz_local' variable
# a list of timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# more info at http://pytz.sourceforge.net/

tz_utc = pytz.utc
tz_local = pytz.timezone('Europe/Berlin')

# SIMPLE FUNCTIONS

# DATETIME --> STRING
def datetime_to_string(dt_any):
    str_any = dt_any.strftime(config.FMT_DT_TO_STR)
    return str_any
    
# STRING --> DATETIME
def utc_string_to_utc_datetime(str_utc):
    dt_utc = datetime.strptime(str_utc, config.FMT_STR_TO_DT)
    return dt_utc

# LOCAL DATETIME --> UTC DATETIME
def local_datetime_to_utc_datetime(dt_local):
    dt_utc = dt_local.astimezone(tz_utc)
    return dt_utc

# UTC DATETIME --> LOCAL DATETIME
def utc_datetime_to_local_datetime(dt_utc):
    dt_local = dt_utc.astimezone(tz_local)
    return dt_local

# NAIVE STRING --> NAIVE DATETIME
def naive_string_to_naive_datetime(naive_str):
    naive_dt = datetime.strptime(naive_str, config.FMT_STR_TO_DT)
    return naive_dt
    
# NAIVE LOCAL DATETIME --> LOCAL DATETIME
def naive_local_datetime_to_local_datetime(naive_dt_local):
    dt_local = tz_local.localize(naive_dt_local)
    return dt_local
    
# NAIVE UTC DATETIME --> UTC DATETIME
def naive_utc_datetime_to_utc_datetime(naive_dt_utc):
    dt_utc = tz_utc.localize(naive_dt_utc)
    return dt_utc
    
# COMPOSITE FUNCTIONS

# deprecated: Django 1.4 supports storing TZ information with the datetime
def naive_local_datetime_to_utc_string(naive_dt_local):
    dt_local = naive_local_datetime_to_local_datetime(naive_dt_local)
    dt_utc = local_datetime_to_utc_datetime(dt_local)
    str_utc = datetime_to_string(dt_utc)
    return str_utc

# always UTC datetime strings in the RESTful API
def local_datetime_to_utc_string(dt_local):
    dt_utc = local_datetime_to_utc_datetime(dt_local)
    str_utc = datetime_to_string(dt_utc)
    return str_utc

# always convert to the local TZ before storing the resource
def utc_string_to_local_datetime(str_utc):
    dt_utc = utc_string_to_utc_datetime(str_utc)
    dt_local = utc_datetime_to_local_datetime(dt_utc)
    return dt_local

