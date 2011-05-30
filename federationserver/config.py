DEBUG = True

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

if DEBUG:
    TFA_PROTOCOL = 'http'
    TFA_HOST = 'localhost'
    TFA_PORT = '8080'
else:
    TFA_PROTOCOL = 'https'
    TFA_HOST = 'conet-testbed-federation.appspot.com'
    TFA_PORT = '80'