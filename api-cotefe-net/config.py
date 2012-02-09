import os
import logging

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

SERVER_NAME = os.environ['SERVER_NAME']
DEBUG = SERVER_NAME == 'localhost'
logging.info("SERVER_NAME: %s" % os.environ['SERVER_NAME'])
logging.info("Starting application in DEBUG mode: %s" % DEBUG)

FEDERATION_SERVER_URL = 'http://api.cotefe.net'

if DEBUG:
    FEDERATION_SERVER_URL = 'http://localhost:8080'
    TESTBED_SERVER_URL_1 = 'http://locahost:8001'
    TESTBED_SERVER_URL_2 = 'http://locahost:8002'
else:
    FEDERATION_SERVER_URL = 'https://api.cotefe.net'
    TESTBED_SERVER_URL_1 = 'https://www.twist.tu-berlin.de:8001'
    TESTBED_SERVER_URL_2 = 'http://example.org'

MEDIA_TYPE = 'application/json'

JANRAIN_URL = 'https://rpxnow.com/api/v2/auth_info'
JANRAIN_API_KEY = '651255fba56215a853a4d8ce1b6e1d632947ce74'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

CONTENT_TYPE = 'application/json'
CHARSET = 'utf8'

FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S+0000'

# initialization data

FEDERATION_NAME = 'COTEFE'
FEDERATION_DESCRIPTION = 'The goal of the CONET Testbed Federation (CTF) Task is to address some of these roadblocks by developing a software platform that will enable convenient access to the experimental resources of multiple testbeds organized in a federation of autonomous entities.'

TESTBED_NAME_1 = 'TWIST'
TESTBED_DESCRIPTION_1 = 'The TKN Wireless Indoor Sensor network Testbed (TWIST), developed by the Telecommunication Networks Group (TKN) at the Technische Universitaet Berlin, is a scalable and flexible testbed architecture for experimenting with wireless sensor network applications in an indoor setting.'
TESTBED_ORGANIZATION_1 = 'TU Berlin'

TESTBED_NAME_2 = 'WISEBED'
TESTBED_DESCRIPTION_2 = 'The WISEBED project is a joint effort of nine academic and research institutes across Europe.'
TESTBED_ORGANIZATION_2 = 'TU Delft'

PLATFORM_NAME_1 = 'eyesIFXv20'
PLATFORM_DESCRIPTION_1 = 'eyesIFXv20'

PLATFORM_NAME_2 = 'eyesIFXv21'
PLATFORM_DESCRIPTION_2 = 'eyesIFXv21'

PLATFORM_NAME_3 = 'TmoteSky'
PLATFORM_DESCRIPTION_3 = 'TmoteSky'

PLATFORM_NAME_4 = 'TelosB'
PLATFORM_DESCRIPTION_4 = 'TelosB'

PLATFORM_NAME_5 = 'TelosA'
PLATFORM_DESCRIPTION_5 = 'TelosA'

PLATFORM_NAME_6 = 'Roomba'
PLATFORM_DESCRIPTION_6 = 'Roomba'