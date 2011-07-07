from django.utils import simplejson as json
from testbedserver.settings import *

from django.http import HttpResponse
import uuid
import logging
from datetime import datetime, tzinfo
import pytz

# UTILITY FUNCTIONS

def build_url(protocol = SERVER_PROTOCOL, host = SERVER_HOST, port = SERVER_PORT, path = '/'):
    return protocol + '://' + host + ':' + port + path
    
def serialize(dict_or_list, format = 'json'):
    if format == 'json':
        return json.dumps(dict_or_list, ensure_ascii = JSON_ENSURE_ASCII, indent = JSON_INDENT) + '\n'
        # return json.dumps(dict_or_list) + '\n'
    else:
        pass
    
def deserialize(string, format = 'json'):
    if format == 'json':
        return json.loads(string)
    else:
        pass
    
def generate_id():
    # logging.debug('uid start')
    id = uuid.uuid4().hex[:UID_LENGTH]
    # logging.debug('uid done')
    return id


# UTC time zone
utc = pytz.utc

# Europe/Berlin time zone
berlin = pytz.timezone('Europe/Berlin')

# datetime string formats
FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S%z'
FMT_STR_TO_DT = '%Y-%m-%dT%H:%M:%S+0000'

def utc_datetime_to_utc_string(dt):
    return utc.localize(dt).strftime(FMT_DT_TO_STR)

def naive_string_to_utc_datetime(dt_str):
    return utc.localize(datetime.strptime(dt_str, FMT_STR_TO_DT))

def utc_string_to_utc_datetime(dt_str):
    return datetime.strptime(dt_str, FMT_STR_TO_DT)

def get_dt_now_utc():
    dt_now_berlin = berlin.localize(datetime.now())
    dt_now_utc = dt_now_berlin.astimezone(utc)
    return dt_now_utc
    