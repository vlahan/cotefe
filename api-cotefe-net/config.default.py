import os

SERVER_NAME = os.environ['SERVER_NAME']

if SERVER_NAME == 'api-cotefe-net.appspot.com':
    FEDERATION_SERVER_URL = 'https://api.cotefe.net'
else:
    FEDERATION_SERVER_URL = 'http://192.168.103.114:8080'

MEDIA_TYPE = 'application/json'

JANRAIN_URL = 'https://rpxnow.com/api/v2/auth_info'
JANRAIN_API_KEY = '651255fba56215a853a4d8ce1b6e1d632947ce74'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

CONTENT_TYPE = 'application/json'
CHARSET = 'utf8'

FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S+0000'

FMT_STR_TO_DT = '%Y-%m-%dT%H:%M:%S+0000'
