DEBUG = True

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

if DEBUG:
    TFA_PROTOCOL = 'http'
    TFA_HOST = 'localhost'
    TFA_PORT = '8080'
    TAA_PROTOCOL = 'http'
    TAA_HOST = 'localhost'
    TAA_PORT = '8001'
else:
    TFA_PROTOCOL = 'https'
    TFA_HOST = 'conet-testbed-federation.appspot.com'
    TFA_PORT = '80'
    TAA_PROTOCOL = 'https'
    TAA_HOST = 'www.twist.tu-berlin.de'
    TAA_PORT = '8001'