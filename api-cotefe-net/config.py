import os
import logging

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SERVER_NAME = os.environ['SERVER_NAME']
DEBUG = SERVER_NAME == 'localhost'
# logging.info("SERVER_NAME: %s" % os.environ['SERVER_NAME'])
logging.info("DEBUG mode: %s" % DEBUG)

if DEBUG:
    FEDERATION_SERVER_URL = 'http://localhost:8080'
else:
    FEDERATION_SERVER_URL = 'https://api.cotefe.net'

MEDIA_TYPE = 'application/json'

JANRAIN_URL = 'https://rpxnow.com/api/v2/auth_info'
JANRAIN_API_KEY = '651255fba56215a853a4d8ce1b6e1d632947ce74'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

CONTENT_TYPE = 'application/json'
CHARSET = 'utf8'

FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S+0000'
