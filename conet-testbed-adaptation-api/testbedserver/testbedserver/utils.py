from django.utils import simplejson as json
from testbedserver.config import *
from django.http import HttpResponse
import uuid
import logging

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
    
def generate_uid():
    logging.debug('uid start')
    uri_uuid = uuid.uuid4().hex[:8]
    logging.debug('uid done')
    return uri_uuid
    