import urllib

import config
import utils

from models import User, Application, OAuth2Session
from handlers import BaseHandler

class OAuth2Authorize(BaseHandler):
    def get(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            client_id = self.request.get('client_id')
            response_type = self.request.get('response_type')
            redirect_uri = self.request.get('redirect_uri')
            application_list = Application.all().filter('client_id =', client_id).fetch(1)
            application = application_list[0]
            if response_type not in ['code', 'token']:
                error = {
                    'status': 400,
                    'message': "Ah, response_type is not valid! (must be either \"code\" or \"token\")",
                }
                self.response.status = '400'
                self.response.out.write(utils.serialize(error))
            else:         
                context = {
                   'user': user,
                   'application': application,
                   'client_id': client_id,
                   'redirect_uri': redirect_uri,
                   'response_type': response_type,
                }
                self.render_response('oauth2/auth.html', **context)              
        else:
            params = {
                'next': urllib.quote('%s%s' % (config.FEDERATION_SERVER_URL, self.request.path_qs), ''),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            client_id = self.request.get('client_id')
            response_type = self.request.get('response_type')
            redirect_uri = self.request.get('redirect_uri')
            application_list = Application.all().filter('client_id =', client_id).fetch(1)
            application = application_list[0]
            if self.request.get('authorize') == 'yes':
                if response_type == 'token':
                    oauth2session = OAuth2Session()
                    oauth2session.application = application
                    oauth2session.user = user
                    oauth2session.access_token = utils.generate_hash()
                    oauth2session.put()            
                    params = {
                        'access_token': oauth2session.access_token,
                        'token_type': 'Bearer',
                        'expires_in': 3600
                    }
                    self.redirect(str('%s?%s' % (redirect_uri, urllib.urlencode(params))))
                elif response_type == 'code':
                    oauth2session = OAuth2Session()
                    oauth2session.application = application
                    oauth2session.user = user
                    oauth2session.code = utils.generate_hash()
                    oauth2session.put()            
                    params = {
                        'code': oauth2session.code,
                    }
                    self.redirect(str('%s?%s' % (redirect_uri, urllib.urlencode(params))))
                else:
                    error = {
                        'status': 400,
                        'message': "Ah, response_type is not valid! (must be either \"code\" or \"token\")",
                    }
                    self.response.status = '400'
                    self.response.out.write(utils.serialize(error))
            else:
                error = {
                    'status': 401,
                    'message': "Ah, you didn't grant authorization!",
                }
                self.response.status = '401'
                self.response.out.write(utils.serialize(error))
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class OAuth2Token(BaseHandler):
    
    def post(self):
        
        grant_type = self.request.get('grant_type')
        code = self.request.get('code')
        redirect_uri = self.request.get('redirect_uri')
        oauth2session_list = OAuth2Session.all().filter('code =', code).fetch(1)
        oauth2session = oauth2session_list[0]
        oauth2session.access_token = utils.generate_hash()
        oauth2session.refresh_token = utils.generate_hash()
        oauth2session.put()
        params = {
            'access_token': oauth2session.access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token' : oauth2session.refresh_token,
        }
        self.response.headers['Content-Type'] = '%s; charset=%s' % (config.CONTENT_TYPE, config.CHARSET)
        self.response.out.write(utils.serialize(params))