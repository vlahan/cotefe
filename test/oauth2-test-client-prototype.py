import httplib2
import urllib
import json
import urlparse

USERNAME = "soundcloud@claudiodonzelli.com"
PASSWORD = "gioconda1981"

AUTHORIZATION_ENDPOINT = "https://soundcloud.com/connect"
LOGIN_ENDPOINT =         "https://soundcloud.com/connect/login"
TOKEN_ENDPOINT =         "https://api.soundcloud.com/oauth2/token"
CLIENT_ID =              "48b5ff33439c7b611448870357fa596b"
CLIENT_SECRET =          "1421d3c532c6da9d05aca5eb29c08b70"
RESPONSE_TYPE =          "code"
REDIRECTION_URI =        "http://anyone-can-play-guitar.appspot.com/"
GRANT_TYPE =             "authorization_code"
TARGET_RESOURCE =        "https://api.soundcloud.com/me/tracks"

http = httplib2.Http()

# AUTHORIZATION REQUEST

query = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, redirect_uri=REDIRECTION_URI)

url = AUTHORIZATION_ENDPOINT + "?" + urllib.urlencode(query)

# print url

response, content = http.request(url)

# print json.dumps(response, indent=4)

# LOGIN REQUEST (CODE REQUEST)

params = dict(response_type=RESPONSE_TYPE, client_id=CLIENT_ID, redirect_uri=REDIRECTION_URI, username=USERNAME, password=PASSWORD)

url = LOGIN_ENDPOINT

response, content = http.request(url, "POST", urllib.urlencode(params))
                                 
# print json.dumps(response, indent=4)

# ACCESS TOKEN REQUEST

oauth_code = dict([part.split('=') for part in urlparse.urlparse(response['location']).query.split('&')])['code']

params = dict(grant_type=GRANT_TYPE, client_id=CLIENT_ID, code=oauth_code, redirect_uri=REDIRECTION_URI)

response, content = http.request(TOKEN_ENDPOINT, "POST", urllib.urlencode(params))

# print json.dumps(response, indent=4)

# print json.dumps(json.loads(content), indent=4)

# GETTING ACCESS TO TARGET RESOURCE

query = dict(oauth_token = json.loads(content)['access_token'], limit = 1)

url = TARGET_RESOURCE + ".json?" + urllib.urlencode(query)

print url

response, content = http.request(url)

print json.dumps(response, indent=4)

print json.dumps(json.loads(content), indent=4)
