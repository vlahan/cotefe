import httplib2
import urllib
import json
import urlparse

USERNAME = "claudiodonzelli"
PASSWORD = "password"

AUTHORIZATION_ENDPOINT = "http://localhost:8080/auth"
LOGIN_ENDPOINT =         "http://localhost:8080/login"
TOKEN_ENDPOINT =         "http://localhost:8080/token"
CLIENT_ID =              "29ed15a2d4de47f49b506b182c4defb9"
CLIENT_SECRET =          "bbbbcb409ea34ad49145a09441da35dd"
RESPONSE_TYPE =          "code"
CALLBACK_URI =           "http://localhost:8081/callback"
GRANT_TYPE =             "authorization_code"
TARGET_RESOURCE =        "http://localhost:8080/api/"

http = httplib2.Http()
# AUTHORIZATION REQUEST
query = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, callback_uri=CALLBACK_URI)
url = AUTHORIZATION_ENDPOINT + "?" + urllib.urlencode(query)
print url
response, content = http.request(url, "GET")
print json.dumps(response, indent=4)
# LOGIN REQUEST (CODE REQUEST)
params = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, callback_uri=CALLBACK_URI, username=USERNAME, password=PASSWORD)
url = LOGIN_ENDPOINT
response, content = http.request(url, "POST", urllib.urlencode(params))                                
print json.dumps(response, indent=4)
# ACCESS TOKEN REQUEST
oauth_code = dict([part.split('=') for part in urlparse.urlparse(response['location']).query.split('&')])['code']
params = dict(grant_type=GRANT_TYPE, client_id=CLIENT_ID, code=oauth_code, callback_uri=CALLBACK_URI)
response, content = http.request(TOKEN_ENDPOINT, "POST", urllib.urlencode(params))
# print json.dumps(response, indent=4)
print json.dumps(json.loads(content), indent=4)
# RESOURCE ACCESS
query = dict(oauth_token = json.loads(content)['access_token'])
url = TARGET_RESOURCE + ".json?" + urllib.urlencode(query)
response, content = http.request(url, "GET")
# print json.dumps(response, indent=4)
print json.dumps(json.loads(content), indent=4)
