from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
import urllib
import urllib2
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

class OpenIdTokenHandler(webapp.RequestHandler):
    def post(self):
        api_params = {
                      'token': self.request.get('token'),
                      'apiKey': '87ec12a943eecb9a7675b714603b014f06777b2f',
                      'format': 'json'
        }
        
        http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params))
        auth_info_json = http_response.read()
        auth_info = json.loads(auth_info_json)
            
        if auth_info['stat'] == 'ok':
            template_values = { 'openid': auth_info['profile']['identifier'], 'auth_info': json.dumps(auth_info, indent=4) }
            logging.info(json.dumps(template_values))
            
            path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
            logging.info(path)
            
            self.response.out.write(template.render(path, template_values))
        else:
            self.response.out.write('An error occured: ' + auth_info['err']['msg'])