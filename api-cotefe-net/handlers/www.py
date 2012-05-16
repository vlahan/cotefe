import urllib

import config
import utils

from models import User, OpenIDIdentity, Application, OAuth2Session
from handlers import BaseHandler

class Login(BaseHandler):
    
    def get(self):
        if self.session.get('username'):
            self.redirect(str(self.request.get('next')) or '/account')
        else:
            context = {
                'next': urllib.quote(self.request.get('next'), ''),
            }
            self.render_response('login.html', **context)
            
    def post(self):
        username = self.request.get('username')
        user_list = User.all().filter('username =', username).fetch(1)
        if len(user_list) > 0:
            user = user_list[0]
            self.session['username'] = user.username
            self.redirect(str(self.request.get('next')) or '/account')
        else:
            params = {
                'next': self.request.get('next'),
            }
            self.redirect(str('%s?%s' % ('/login', urllib.urlencode(params))))

class Account(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            context = {
               'user': user
            }
            self.render_response('account.html', **context)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            user.first = self.request.get('first')
            user.last = self.request.get('last')
            user.email = self.request.get('email')
            user.organization = self.request.get('organization')
            user.put()
            self.redirect(self.request.referer)
        
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Identities(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            
            # get the user
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            
            identities = OpenIDIdentity.all().filter('user =', user).fetch(10)
                
            context = {
                'user': user,
                'identities': identities,
                'server_url' : config.FEDERATION_SERVER_URL,
                'next': urllib.quote('%s%s' % (config.FEDERATION_SERVER_URL, self.request.path), ''),
            }
            self.render_response('identities.html', **context)
        
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            
            identity_id = self.request.get('identity_id')
            
            OpenIDIdentity.get_by_id(int(identity_id)).delete()
            
            self.redirect(self.request.referer)
        
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/login', urllib.urlencode(params)))
                        
class Sessions(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            sessions = OAuth2Session.all().filter('user =', user).fetch(10)
            context = {
                'user': user,
                'sessions': sessions,
            }
            self.render_response('sessions.html', **context)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            session_id = self.request.get('session_id')
            OAuth2Session.get_by_id(int(session_id)).delete()
            self.redirect(self.request.referer)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
            
class Applications(BaseHandler):

    def get(self):

        if self.session.get('username'):
            
            username = self.session.get('username')
            user = User.all().filter('username =', username).fetch(1)[0]
            
            applications = Application.all().filter('owner =', user).fetch(10)
            
            context = {
                'user': user,
                'applications': applications,
            }
            self.render_response('applications.html', **context)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))

    def post(self):

        if self.session.get('username'):
            
            if self.request.get('submit') == 'Add':
                
                username = self.session.get('username')
                user_list = User.all().filter('username =', username).fetch(1)
                user = user_list[0]
                
                name = self.request.get('name')
                redirect_uri = self.request.get('redirect_uri')
                client_id = utils.generate_hash()
                client_secret = utils.generate_hash()
                
                application = Application()
                application.name = name
                application.redirect_uri = redirect_uri
                application.client_id = client_id
                application.client_secret = client_secret
                application.owner = user
                application.put()
                
                self.redirect(self.request.referer)
                
            elif self.request.get('submit') == 'Remove':
                
                application_id = self.request.get('application_id')
                Application.get_by_id(int(application_id)).delete()
                
                self.redirect(self.request.referer)
                
        else:
            
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Logout(BaseHandler):
    
    def get(self):
        
        try:
            del self.session['username']
        except:
            pass
        self.redirect(self.request.referer or '/account')