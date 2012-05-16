import urllib

from google.appengine.api import urlfetch

import config
import utils

from models import User, OpenIDIdentity
from handlers import BaseHandler

class OpenIDLogin(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            self.redirect(str(urllib.unquote(self.request.get('next'))) or '/account')
        else:
            context = {
                'server_url': config.FEDERATION_SERVER_URL,
                'next': self.request.get('next') or '/account',
            }
            self.render_response('openid/login.html', **context)
           
class OpenIDCallback(BaseHandler):
        
    def post(self):
        
        token = self.request.get('token')
        api_params = {
            'token': token,
            'apiKey': config.JANRAIN_API_KEY,
            'format': 'json',
        }
        result = urlfetch.fetch(url=config.JANRAIN_URL, method=urlfetch.POST, payload=urllib.urlencode(api_params), validate_certificate=False)
        auth_info_json = result.content
        auth_info = utils.deserialize(auth_info_json)
        profile = auth_info['profile']
        provider = profile['providerName']
        identifier = profile['identifier']
        identity_list = OpenIDIdentity.all().filter('identifier =', identifier).fetch(1)
        if len(identity_list) > 0:
            identity = identity_list[0]
            username = identity.user.username            
            self.session['username'] = username
            self.redirect(str(self.request.get('next')) or '/account')
        else:
            params = {
                    'next': self.request.get('next'),
                    'provider' : provider,
                    'identifier': identifier
            }
            if self.session.get('username'):
                self.redirect(str('%s?%s' % ('/openid/connect', urllib.urlencode(params))))
            else:
                self.redirect(str('%s?%s' % ('/openid/new', urllib.urlencode(params))))
            
class OpenIDNew(BaseHandler):
    
    def get(self):
        
        provider = self.request.get('provider')
        identifier = self.request.get('identifier')
        next = self.request.get('next')
        context = {
           'next': next,
           'provider': provider,
           'identifier': identifier,
        }
        self.render_response('openid/new.html', **context)
            
    def post(self):
        
        next = self.request.get('next')
        provider = self.request.get('provider')
        identifier = self.request.get('identifier')
        username = self.request.get('username')
        
        user_list = User.all().filter('username = ', username).fetch(1)
        if len(user_list) > 0:
            context = {
               'next': next,
               'provider': provider,
               'identifier': identifier,
               'message': 'Oops! The username \"%s\" is taken. If it belongs to you please log in and add it to your identities.' % (username, ),
            }
            self.render_response('openid/new.html', **context)
        else:
            user = User()
            user.username = username
            user.admin = False
            user.put()
            identity = OpenIDIdentity()
            identity.user = user
            identity.provider = provider
            identity.identifier = identifier
            identity.put()
            self.session['username'] = user.username
            self.redirect(str('%s' % (next, )))
        
class OpenIDConnect(BaseHandler):
    
    def get(self):
        
        provider = self.request.get('provider')
        identifier = self.request.get('identifier')
        next = self.request.get('next')
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            context = {
               'user': user,
               'next': next,
               'provider': provider,
               'identifier': identifier,
            }
            self.render_response('openid/connect.html', **context)
        else:
            self.redirect('/openid/login?next=%s' % urllib.quote('%s%s' % (config.FEDERATION_SERVER_URL, self.request.path), ''))
            
    def post(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            next = self.request.get('next')
            provider = self.request.get('provider')
            identifier = self.request.get('identifier')
            identity = OpenIDIdentity()
            identity.user = user
            identity.provider = provider
            identity.identifier = identifier
            identity.put()
            self.redirect(str('%s' % (next, )))
        else:
            self.redirect(str('/openid/login?next=%s' % urllib.quote('%s%s' % (config.FEDERATION_SERVER_URL, self.request.path), '')))