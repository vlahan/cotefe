import httplib2
import urllib
import json
import urlparse
import logging
import webbrowser

CLIENT_ID =              "389368352525.apps.googleusercontent.com"
CLIENT_SECRET =          "KvYYC1_UERVMYqWmDc8FEj_o"

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
RESPONSE_TYPE =          "code"
# RESPONSE_TYPE =          "token"
REDIRECTION_URI =        "http://something.cotefe.net/oauth2callback"
SCOPE =                  "http://something.cotefe.net"

TOKEN_ENDPOINT =         "https://accounts.google.com/o/oauth2/token"
GRANT_TYPE =             "authorization_code"

TARGET_RESOURCE =        "http://something.cotefe.net/"

OAUTH_TOKEN =           "1/zHilsLP6t9OIQmOWPXvdXI7ydNu7oPxZas_ZtU3rgRU"

REQUEST_ACCESS_TOKEN = 1
AUTHORIZATION_HEADER = 0

http = httplib2.Http()

if REQUEST_ACCESS_TOKEN:
    query = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, redirect_uri=REDIRECTION_URI, scope=SCOPE, hd='cotefe.net')
    url = AUTHORIZATION_ENDPOINT + "?" + urllib.urlencode(query)
    webbrowser.open(url)
    oauth_code = raw_input('Enter OAuth code: ')
    params = dict(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=oauth_code, redirect_uri=REDIRECTION_URI, grant_type=GRANT_TYPE)
    response, content = http.request(TOKEN_ENDPOINT, "POST", urllib.urlencode(params), headers = { "Content-Type" : "application/x-www-form-urlencoded"})
    oauth_token = json.loads(content)['access_token']
    # print oauth_token
    # response, content = http.request(TOKEN_ENDPOINT, "POST", urllib.urlencode(params), headers = { "Content-Type" : "application/x-www-form-urlencoded"})
    # oauth_token = json.loads(content)['access_token']
    print oauth_token
    print
else:
    oauth_token = OAUTH_TOKEN
    
if AUTHORIZATION_HEADER:
    response, content = http.request(TARGET_RESOURCE, "GET", headers = {"Authorization" : "OAuth " + oauth_token})
    print content
else:
    query = { "oauth_token" : oauth_token }
    webbrowser.open(TARGET_RESOURCE + "?" + urllib.urlencode(query))