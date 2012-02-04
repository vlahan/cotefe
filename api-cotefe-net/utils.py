import uuid
import logging
import json
import hashlib

import config

def build_url(server_url = config.FEDERATION_SERVER_URL, path = '/'):
    return '%s%s' % (server_url, path)
   
def serialize(dict_or_list, format = 'json'):
    if format == 'json':
        return json.dumps(dict_or_list, ensure_ascii = config.JSON_ENSURE_ASCII, indent = config.JSON_INDENT)
    elif format == 'xml':
        pass
   
def deserialize(string, format = 'json'):
    if format == 'json':
        return json.loads(string)
    else:
        pass
   
def convert_datetime_to_string(dt):
    return dt.strftime(config.FMT_DT_TO_STR)

def encrypt(word):
    return hashlib.md5(word).hexdigest()

def generate_hash():
    return uuid.uuid4().hex
   

# from datetime import datetime, tzinfo
# import pytz
# 
# # UTC time zone
# utc = pytz.utc
# 
# # Europe/Berlin time zone
# berlin = pytz.timezone('Europe/Berlin')
# 
# # datetime string formats
# FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S%z'
# FMT_STR_TO_DT = '%Y-%m-%dT%H:%M:%S+0000'
# 
# def berlin_datetime_to_berlin_string(dt):
#    dt_berlin = berlin.localize(dt)
#    return dt_berlin.strftime(FMT_DT_TO_STR)
# 
# def utc_datetime_to_utc_string(dt):
#    dt_utc = utc.localize(dt)
#    return dt_utc.strftime(FMT_DT_TO_STR)
# 
# def berlin_datetime_to_utc_string(dt):
#    dt_berlin = berlin.localize(dt)
#    dt_utc = dt_berlin.astimezone(utc)
#    return dt_utc.strftime(FMT_DT_TO_STR)
# 
# def naive_string_to_utc_datetime(dt_str):
#    return berlin.localize(datetime.strptime(dt_str, FMT_STR_TO_DT))
# 
# def utc_string_to_utc_datetime(dt_str):
#    return datetime.strptime(dt_str, FMT_STR_TO_DT)
# 
# def get_dt_now_utc():
#    dt_now_berlin = berlin.localize(datetime.now())
#    dt_now_utc = dt_now_berlin.astimezone(utc)
#    return dt_now_utc
