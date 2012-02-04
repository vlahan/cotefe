import logging
import webapp2
from webapp2_extras import sessions
from webapp2_extras import jinja2
import urllib
import json

import cgi
import uuid

import os

# jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.api import urlfetch

import config
from utils import serialize, encrypt, generate_hash

from models import *

# for DEBUG purpose only - MUST disable on production
class DatastoreInitialization(webapp2.RequestHandler):

    def get(self):
        
        # cleaning the datastore
        # for user in User.all(): user.delete()   
        # for identity in OpenIDIdentity.all(): identity.delete()  
        # for application in Application.all(): application.delete()
        # for session in OAuth2Session.all(): session.delete()
        # for federation in Federation.all(): federation.delete()
        # for testbed in Testbed.all(): testbed.delete()
        # for platform in Platform.all(): platform.delete()
        # for project in Project.all(): project.delete()
                
        # initial data
#        User(username = 'demo', password = encrypt('demo')).put()
#        User(username = 'vlado', password = encrypt('conet')).put()
#        User(username = 'claudio', password = encrypt('conet')).put()
#        User(username = 'sanjeet', password = encrypt('conet')).put()
        
        Application(
            name = 'COTEFE Web Client',
            client_id = '661b6d2134744642baae57f7aa535802',
            client_secret = '1b2ccad4f2604db6b9b70f728254d3cd',
            redirect_uri = 'http://web.cotefe.net/',
        ).put()
        
        Federation(
            name = config.FEDERATION_NAME,
            description = config.FEDERATION_DESCRIPTION,
        ).put()
        
        Testbed(
            name = config.TESTBED_NAME_1,
            description = config.TESTBED_DESCRIPTION_1,
            organization = config.TESTBED_ORGANIZATION_1,
            server_url = config.TESTBED_SERVER_URL_1,
        ).put()
        
        Testbed(
            name = config.TESTBED_NAME_2,
            description = config.TESTBED_DESCRIPTION_2,
            organization = config.TESTBED_ORGANIZATION_2,
            server_url = config.TESTBED_SERVER_URL_2,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_1,
            description = config.PLATFORM_DESCRIPTION_1,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_2,
            description = config.PLATFORM_DESCRIPTION_2,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_3,
            description = config.PLATFORM_DESCRIPTION_3,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_4,
            description = config.PLATFORM_DESCRIPTION_4,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_5,
            description = config.PLATFORM_DESCRIPTION_5,
        ).put()
        
        Platform(
            name = config.PLATFORM_NAME_6,
            description = config.PLATFORM_DESCRIPTION_6,
        ).put()
        
        self.response.out.write('Datastore has been initialized!')


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

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
        password = self.request.get('password')
        password_hash = encrypt(password)
        user_list = User.all().filter('username =', username).filter('password =', password_hash).fetch(1)
        if len(user_list) > 0:
            user = user_list[0]
            self.session['username'] = user.username
            self.redirect(str(self.request.get('next')) or '/account')
        else:
            params = {
                'next': self.request.get('next'),
            }
            self.redirect(str('%s?%s' % ('/login', urllib.urlencode(params))))

class OpenIDLogin(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            self.redirect(str(self.request.get('next')) or '/account')
        else:
            context = {
                'server_url' : self.request.host_url,
                'next': urllib.quote(self.request.get('next'), '') or '/account',
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
        auth_info = json.loads(auth_info_json)
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
            self.redirect('/openid/login?next=%s' % urllib.quote(self.request.uri, ''))
            
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
            self.redirect(str('/openid/login?next=%s' % urllib.quote(self.request.uri, '')))
            
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
                self.response.out.write(serialize(error))
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
                'next': self.request.uri,
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
                    oauth2session.access_token = generate_hash()
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
                    oauth2session.code = generate_hash()
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
                    self.response.out.write(serialize(error))
            else:
                error = {
                    'status': 401,
                    'message': "Ah, you didn't grant authorization!",
                }
                self.response.status = '401'
                self.response.out.write(serialize(error))
        else:
            params = {
                'next': self.request.uri,
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class OAuth2Token(BaseHandler):
    
    def post(self):
        
        grant_type = self.request.get('grant_type')
        code = self.request.get('code')
        redirect_uri = self.request.get('redirect_uri')
        oauth2session_list = OAuth2Session.all().filter('code =', code).fetch(1)
        oauth2session = oauth2session_list[0]
        oauth2session.access_token = generate_hash()
        oauth2session.refres_token = generate_hash()
        oauth2session.put()
        params = {
            'access_token': oauth2session.access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token' : oauth2session.refres_token,
        }
        self.response.headers['Content-Type'] = '%s; charset=%s' % (config.CONTENT_TYPE, config.CHARSET)
        self.response.out.write(serialize(params))
        
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
                'next': self.request.uri,
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
                'next': self.request.uri,
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
                'server_url' : self.request.host_url,
                'next': urllib.quote(self.request.uri, ''),
            }
            self.render_response('identities.html', **context)
        
        else:
            params = {
                'next': self.request.uri,
            }
            self.redirect('%s?%s' % ('/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            
            identity_id = self.request.get('identity_id')
            
            OpenIDIdentity.get_by_id(int(identity_id)).delete()
            
            self.redirect(self.request.referer)
        
        else:
            params = {
                'next': self.request.uri,
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
                'next': self.request.uri,
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):
        
        if self.session.get('username'):
            session_id = self.request.get('session_id')
            OAuth2Session.get_by_id(int(session_id)).delete()
            self.redirect(self.request.referer)
        else:
            params = {
                'next': self.request.uri,
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Docs(BaseHandler):
    
    def get(self):
        
        if self.session.get('username'):
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            context = {
                'user': user,
            }
            self.render_response('docs.html', **context)
            
        else:
            params = {
                'next': self.request.uri,
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Logout(BaseHandler):
    
    def get(self):
        
        try:
            del self.session['username']
        except:
            pass
        self.redirect(self.request.referer or '/account')


class OAuth2RESTJSONHandler(webapp2.RequestHandler):
    
    def add_headers(self):
        self.response.headers['Content-Type'] = '%s; charset=%s' % (config.CONTENT_TYPE, config.CHARSET)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
    
    def dispatch(self):
        
        self.add_headers()
        
        if self.request.get('access_token'):
            oauth2session_list = OAuth2Session.all().filter('access_token =', self.request.get('access_token')).fetch(1)
            if len(oauth2session_list) > 0:
                oauth2session = oauth2session_list[0]
                self.user = oauth2session.user
                webapp2.RequestHandler.dispatch(self)
            else:
                error = {
                    'status': 401,
                    'message': "Ah, your access_token is not valid!"
                }
                self.response.status = '401'
                self.response.out.write(serialize(error))
        else:
            error = {
                'status': 401,
                'message': "Ah, you need an access_token!"
            }
            self.response.status = '401'
            self.response.out.write(serialize(error))
            
# ME (current user)

class MeHandler(OAuth2RESTJSONHandler):   

    def get(self):
        
        self.response.out.write(serialize(self.user.to_dict()))
        
# USER
            
class UserCollectionHandler(OAuth2RESTJSONHandler):
        
    def get(self):
        
        user_list = list()
        for user in User.all():
            user_list.append(user.to_dict(head_only = True))
        self.response.out.write(serialize(user_list))

class UserResourceHandler(OAuth2RESTJSONHandler):
    
    def get(self, user_id):
        
        user = User.get_by_id(int(user_id))
        self.response.out.write(serialize(user.to_dict()))
        
# FEDERATION
            
class FederationResourceHandler(OAuth2RESTJSONHandler):
    
    def get(self):
            
        federation = Federation.all().get()
        self.response.out.write(serialize(federation.to_dict()))
            
# TESTBED
            
class TestbedCollectionHandler(OAuth2RESTJSONHandler):
        
    def get(self):
        
        testbed_list = list()
        for testbed in Testbed.all():
            testbed_list.append(testbed.to_dict(head_only = True))
        self.response.out.write(serialize(testbed_list))

class TestbedResourceHandler(OAuth2RESTJSONHandler):
    
    def get(self, testbed_id):
        
        testbed = Testbed.get_by_id(int(testbed_id))
        self.response.out.write(serialize(testbed.to_dict()))
        
# PLATFORM
            
class PlatformCollectionHandler(OAuth2RESTJSONHandler):
    
    def get(self):
        
        platform_list = list()
        for platform in Platform.all():
            platform_list.append(platform.to_dict(head_only = True))
        self.response.out.write(serialize(platform_list))
                
class PlatformResourceHandler(OAuth2RESTJSONHandler):
    
    def get(self, platform_id):
        
        platform = Platform.get_by_id(int(platform_id))
        self.response.out.write(serialize(platform.to_dict()))

# PROJECT

class ProjectCollectionHandler(OAuth2RESTJSONHandler):
    
    def get(self):
        
        project_list = list()
        for project in Project.all().filter('created_by = ', self.user):
            project_list.append(project.to_dict(head_only = True))
        self.response.out.write(serialize(project_list))
            
    def post(self):
        
        project_dict = json.loads(self.request.body)
        project = Project()
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.created_by = self.user
        project.members.append(self.user.key())
        project.put()
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % (project.uri())
        self.response.headers['Content-Location'] = '%s' % (project.uri())
            
class ProjectResourceHandler(OAuth2RESTJSONHandler):
    
    def get(self, project_id):
        
        project = Project.get_by_id(int(project_id))
        self.response.out.write(serialize(project.to_dict()))
                
    def put(self, project_id):
        
        project_dict = json.loads(self.request.body)
        project = Project.get_by_id(int(project_id))
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.put()
        self.response.out.write(serialize(project.to_dict()))
            
    def delete(self, project_id):
        
        project = Project.get_by_id(int(project_id))
        project.delete()
        self.response.status = '204'


        
