import urllib
import urllib2
import json

class OpenIdTokenHandler(webapp.RequestHandler):
    token = self.request.get('token')
    
    api_params = {
                  'token': token,
                  'apiKey': '87ec12a943eecb9a7675b714603b014f06777b2f',
                  'format': 'json',
    }
    
    http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params))
    auth_info_json = http_response.read()
    auth_info = json.loads(auth_info_json)
    
    if auth_info['stat'] == 'ok':
        profile = auth_info['profile']
        identifier = profile['identifier']
        name = profile.get('displayName')
        email = profile.get('email')
        profile_pic_url = profile.get('photo')
        self.response.out.write(identifier)
    else:
        self.response.out.write('An error occured: ' + auth_info['err']['msg']) 