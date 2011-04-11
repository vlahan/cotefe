from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from config import *

# UTILITY FUNCTIONS

def build_url(protocol = TFA_PROTOCOL, host = TFA_HOST, port = TFA_PORT, path = '/'):
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