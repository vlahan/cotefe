import json
from datetime import datetime
import pytz
from cotefe import config

# (de)serialization of python dictionaries and lists into JSON format
# more info at http://docs.python.org/library/json.html

def serialize(dict_or_list):
    return json.dumps(dict_or_list, ensure_ascii = config.JSON_ENSURE_ASCII, indent = config.JSON_INDENT) + '\n'

def deserialize(string):
    return json.loads(string)

# datetime and time zone utility functions
# testbed admin must set the local time zone first via the 'tz_local' variable
# a list of timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# more info at http://pytz.sourceforge.net/

tz_utc = pytz.utc
tz_local = pytz.timezone(config.TIMEZONE)

# utility functions for formatting of datatime object according to the standard ISO 8601
# more info at http://en.wikipedia.org/wiki/ISO_8601

# BASIC FUNCTIONS

# datetime --> string
def datetime_to_string(dt):
    s = dt.strftime(config.FMT_DT_TO_STR)
    return s
    
# string --> datetime
def string_to_datetime(s):
    dt = datetime.strptime(s, config.FMT_STR_TO_DT)
    return dt

# ADDING TIME ZONE INFORMATION

# naive utc datatime --> utc datetime
def naive_utc_datetime_to_utc_datetime(naive_utc_dt):
    utc_dt = tz_utc.localize(naive_utc_dt)
    return utc_dt

# naive local datetime --> local datetime
def naive_local_datetime_to_local_datetime(naive_local_dt):
    local_dt = tz_local.localize(naive_local_dt)
    return local_dt

# CONVERTING BETWEEN DIFFERENT TIMEZONES

# local datetime --> utc datetime
def local_datetime_to_utc_datetime(local_dt):
    utc_dt = local_dt.astimezone(tz_utc)
    return utc_dt

# utc datetime --> local datetime
def utc_datetime_to_local_datetime(utc_dt):
    local_dt = utc_dt.astimezone(tz_local)
    return local_dt

# COMPOSITE FUNCTIONS

# str --> utc datetime
def string_to_utc_datetime(s):
    naive_utc_dt = string_to_datetime(s)
    utc_dt = naive_utc_datetime_to_utc_datetime(naive_utc_dt)
    return utc_dt