import json
import pytz
import uuid
from datetime import datetime
from api import config

# serialization of python dictionaries and lists into JSON format
# more info at http://docs.python.org/library/json.html

def serialize(obj):
    return json.dumps(obj, ensure_ascii = config.JSON_ENSURE_ASCII, indent = config.JSON_INDENT)

# deserialization of python JSON string into Python object
# more info at http://docs.python.org/library/json.html

def deserialize(string):
    return json.loads(string)
    
# generated random 16 characters strings as identifiers
# more info at http://docs.python.org/library/uuid.html
    
def generate_id():
    return uuid.uuid4().hex

# datetime and time zone utility functions
# testbed admin must set the local time zone first via the 'tz_local' variable
# a list of timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# more info at http://pytz.sourceforge.net/

tz_utc = pytz.utc
tz_local = pytz.timezone(config.TIMEZONE)

# utility functions for formatting of datatime object according to the standard ISO 8601
# more info at http://en.wikipedia.org/wiki/ISO_8601

# BASIC FUNCTIONS

def datetime_to_string(dt):
    s = dt.strftime(config.FMT_DT_TO_STR)
    return s

def string_to_datetime(s):
    dt = datetime.strptime(s, config.FMT_STR_TO_DT)
    return dt

# ADDING TIME ZONE INFORMATION

def naive_datetime_to_utc_datetime(naive_dt):
    utc_dt = tz_utc.localize(naive_dt)
    return utc_dt

def naive_datetime_to_local_datetime(naive_dt):
    local_dt = tz_local.localize(naive_dt)
    return local_dt

# CONVERTING BETWEEN DIFFERENT TIMEZONES

def local_datetime_to_utc_datetime(local_dt):
    utc_dt = local_dt.astimezone(tz_utc)
    return utc_dt

def utc_datetime_to_local_datetime(utc_dt):
    local_dt = utc_dt.astimezone(tz_local)
    return local_dt

# COMPOSITE FUNCTIONS
# please note: Django 1.4 supports storing TZ information with the datetime

def local_string_to_local_datetime(local_str):
    naive_local_dt = string_to_datetime(local_str)
    local_dt = naive_datetime_to_local_datetime(naive_local_dt)
    return local_dt

def local_datetime_to_utc_string(local_dt):
    utc_dt = local_datetime_to_utc_datetime(local_dt)
    utc_string = datetime_to_string(utc_dt)
    return utc_string
    
def utc_string_to_local_string(utc_string):
    naive_utc_dt = string_to_datetime(utc_string)
    utc_dt = naive_datetime_to_utc_datetime(naive_utc_dt)
    local_dt = utc_datetime_to_local_datetime(utc_dt)
    local_string = datetime_to_string(local_dt)
    return local_string

def utc_string_to_local_datetime(utc_string):
    naive_utc_dt = string_to_datetime(utc_string)
    utc_dt = naive_datetime_to_utc_datetime(naive_utc_dt)
    local_dt = utc_datetime_to_local_datetime(utc_dt)
    return local_dt
