from django.utils import simplejson as json
from config import *
from django.http import HttpResponse
import uuid
import logging
from datetime import datetime, tzinfo

# UTILITY FUNCTIONS

def build_url(protocol = SERVER_PROTOCOL, host = SERVER_HOST, port = SERVER_PORT, path = '/'):
    if port == '80':
        return protocol + '://' + host + path
    else:
        return protocol + '://' + host + ':' + port + path
    
def serialize(dict_or_list, format = 'json'):
    if format == 'json':
        return json.dumps(dict_or_list, ensure_ascii = JSON_ENSURE_ASCII, indent = JSON_INDENT)
    else:
        pass
    
def deserialize(string, format = 'json'):
    if format == 'json':
        return json.loads(string)
    else:
        pass
    
def generate_uid():
    # logging.warning('uid start')
    uri_uuid = uuid.uuid4().hex[:UID_LENGTH]
    # logging.warning('uid done')
    return uri_uuid