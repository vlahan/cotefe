import httplib2
import urllib
import json
import urlparse
import logging
import webbrowser

CLIENT_ID =              '389368352525.apps.googleusercontent.com'
CLIENT_SECRET =          'oXKNrB0gJn2V3FL9f8Zg21YU'

AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
RESPONSE_TYPE =          'code'
REDIRECTION_URI =        'http://www.example.org/oauth2callback'
SCOPE =                  'http://something.cotefe.net/'
HD =                     'cotefe.net'
TOKEN_ENDPOINT =         'https://accounts.google.com/o/oauth2/token'
GRANT_TYPE =             'authorization_code'
TARGET_RESOURCE =        'http://something.cotefe.net/'
OAUTH_TOKEN =            '1/zHilsLP6t9OIQmOWPXvdXI7ydNu7oPxZas_ZtU3rgRU'

REQUEST_ACCESS_TOKEN = 1
AUTHORIZATION_HEADER = 1

http = httplib2.Http()

if REQUEST_ACCESS_TOKEN:
    query = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, redirect_uri=REDIRECTION_URI, hd=HD)
    # query = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, redirect_uri=REDIRECTION_URI, scope=SCOPE, hd=HD)

    url = AUTHORIZATION_ENDPOINT + '?' + urllib.urlencode(query)
    print url
    # webbrowser.open(url)
    oauth_code = raw_input('Enter OAuth code: ')
    params = dict(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=oauth_code, redirect_uri=REDIRECTION_URI, grant_type=GRANT_TYPE)
    response, content = http.request(TOKEN_ENDPOINT, 'POST', urllib.urlencode(params), headers = { 'Content-Type' : 'application/x-www-form-urlencoded'})
    oauth_token = json.loads(content)['access_token']
else:
    oauth_token = OAUTH_TOKEN

print oauth_token
    
if AUTHORIZATION_HEADER:
    response, content = http.request(TARGET_RESOURCE, 'GET', headers = {'Authorization' : 'OAuth ' + oauth_token})
    print content
else:
    query = { 'oauth_token' : oauth_token }
    webbrowser.open(TARGET_RESOURCE + '?' + urllib.urlencode(query))