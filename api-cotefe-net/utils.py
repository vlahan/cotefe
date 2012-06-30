import json
import uuid
from datetime import datetime

import config

def build_url(server_url = config.FEDERATION_SERVER_URL, path = '/'):
    return '%s%s' % (server_url, path)
   

# (de)serialization of python dictionaries and lists into JSON format
# more info at http://docs.python.org/library/json.html

def serialize(dict_or_list):
    return json.dumps(dict_or_list, ensure_ascii = config.JSON_ENSURE_ASCII, indent = config.JSON_INDENT) + '\n'

def deserialize(string):
    return json.loads(string)

# generates a 16 digits hex string

def generate_hash():
    return uuid.uuid4().hex


# datetime and time zone utility functions
# developer must set the local time zone first via the 'tz_local' variable
# a list of timezones can be found at https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# more info at http://pytz.sourceforge.net/

# SIMPLE FUNCTIONS

# DATETIME --> STRING
def datetime_to_string(dt_any):
    str_any = dt_any.strftime(config.FMT_DT_TO_STR)
    return str_any
    
# STRING --> DATETIME
def utc_string_to_utc_datetime(str_utc):
    dt_utc = datetime.strptime(str_utc, config.FMT_STR_TO_DT)
    return dt_utc
