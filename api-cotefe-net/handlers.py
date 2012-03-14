import logging
import webapp2
from webapp2_extras import sessions
from webapp2_extras import jinja2
import urllib
import json
import cgi
import uuid
import os

from google.appengine.api import urlfetch
from google.appengine.ext import db

import config
from utils import serialize, encrypt, generate_hash

from models import *

# for DEBUG purpose only - MUST disable on production
class DatastoreInitialization(webapp2.RequestHandler):

    def get(self):
        
        # cleaning the datastore
        for user in User.all(): user.delete()
        
        for identity in OpenIDIdentity.all(): identity.delete()  
        for application in Application.all(): application.delete()
        for session in OAuth2Session.all(): session.delete()
        
        for federation in Federation.all(): federation.delete()
        for testbed in Testbed.all(): testbed.delete()
        for platform in Platform.all(): platform.delete()
        for interface in Interface.all(): interface.delete()
        for sensor in Sensor.all(): sensor.delete()
        for actuator in Actuator.all(): actuator.delete()
        
        for project in Project.all(): project.delete()
        for experiment in Experiment.all(): experiment.delete()
        for image in Image.all(): image.delete()
        for property_set in PropertySet.all(): property_set.delete()
        for virtual_node in VirtualNode.all(): virtual_node.delete()
        for virtual_node_group in VirtualNodeGroup.all(): virtual_node_group.delete()
        for virtual_task in VirtualTask.all(): virtual_task.delete()
        
        Federation(
            name = 'COTEFE',
            description = 'The goal of the CONET Testbed Federation (CTF) Task is to address some of these roadblocks by developing a software platform that will enable convenient access to the experimental resources of multiple testbeds organized in a federation of autonomous entities.',
        ).put()
        
        Testbed(
            name = 'TWIST',
            description = 'The TKN Wireless Indoor Sensor network Testbed (TWIST), developed by the Telecommunication Networks Group (TKN) at the Technische Universitaet Berlin, is a scalable and flexible testbed architecture for experimenting with wireless sensor network applications in an indoor setting.',
            organization = 'TU Berlin',
            homepage = 'https://www.twist.tu-berlin.de:8000',
            server_url = 'https://www.twist.tu-berlin.de:8001',
            background_image_url = 'https://www.twist.tu-berlin.de:8001/uploads/testbed/background.jpg',
            coordinates_mapping_function_x = '-5.5+x*46.9+y+16.6',
            coordinates_mapping_function_y =  '1517-y*16.9-z*78.3',
        ).put()
        
        Testbed(
            name = 'WISEBED',
            description = 'The WISEBED project is a joint effort of nine academic and research institutes across Europe.',
            organization = 'TU Delft',
            server_url = 'http://example.org',
        ).put()
        
        Platform(
            key_name = 'eyesifxv20',
            name = 'eyesIFXv20',
            description = '',
        ).put()
        
        Platform(
            key_name = 'eyesifxv21',
            name = 'eyesIFXv21',
            description = '',
        ).put()
        
        Platform(
            key_name = 'tmotesky',
            name = 'TmoteSky',
            description = '',
        ).put()
        
        Platform(
            key_name = 'telosa',
            name = 'TelosA',
            description = '',
        ).put()
        
        Platform(
            key_name = 'telosb',
            name = 'TelosB',
            description = '',
        ).put()
        
        Interface(
            key_name = 'tinyos',
            name = 'TinyOS',
            description = '',
        ).put()
        
        Interface(
            key_name = 'contiki',
            name = 'Contiki',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'temperature',
            name = 'Temperature',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'pressure',
            name = 'Pressure',
            description = '',
        ).put()
        
        Sensor(
            key_name = 'light',
            name = 'Light',
            description = '',
        ).put()
        
        Actuator(
            key_name = 'sound',
            name = 'Sound',
            description = '',
        ).put()
        
        Actuator(
            key_name = 'led',
            name = 'LED',
            description = '',
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
        oauth2session.access_token = generate_hash()
        oauth2session.refresh_token = generate_hash()
        oauth2session.put()
        params = {
            'access_token': oauth2session.access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token' : oauth2session.refresh_token,
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
                client_id = generate_hash()
                client_secret = generate_hash()
                
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


class OAuth2RESTJSONHandler(webapp2.RequestHandler):
    
    def add_headers(self):
        self.response.headers['Content-Type'] = '%s; charset=%s' % (config.CONTENT_TYPE, config.CHARSET)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Cache-Control, Pragma, Referer, User-Agent'
        self.response.headers['Access-Control-Allow-Credentials'] = 'True'
        self.response.headers['Access-Control-Max-Age'] = '60'
        
    def options(self, allowed_methods):
        self.add_headers()
        
        self.response.status = '204'
        self.response.headers['Allow'] = ', '.join(allowed_methods)
        
    
    def dispatch(self):
        
        self.add_headers()
        
        try:
            access_token = self.request.get('access_token') or self.request.headers['Authorization'].split(' ')[1]
        except:
            access_token = ''
        
        if access_token:
            oauth2session_list = OAuth2Session.all().filter('access_token =', access_token).fetch(1)
            if len(oauth2session_list) == 1:
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
            
            if self.request.method == 'GET':
                webapp2.RequestHandler.dispatch(self)
            else:
                error = {
                    'status': 401,
                    'message': "Ah, you need an access_token!"
                }
                self.response.status = '401'
                self.response.out.write(serialize(error))
            
# ME (current user)

class MeHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self):
        
        try:
            self.response.out.write(serialize(self.user.to_dict()))        
        
        except:
            self.response.status = '404'
# USER
            
class UserCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def get(self):
        
        user_list = list()
        for user in User.all():
            user_list.append(user.to_dict(head_only = True))
        self.response.out.write(serialize(user_list))

class UserResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, user_id):
        
        try:
            user = User.get_by_id(int(user_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(serialize(user.to_dict()))
            
# FEDERATION
            
class FederationResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
            
        try:
            federation = Federation.all().get()
            self.response.out.write(serialize(federation.to_dict()))
        except:
            self.response.status = '404'
            
        
            
# TESTBED
            
class TestbedCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def get(self):
        
        testbed_list = list()
        for testbed in Testbed.all():
            testbed_list.append(testbed.to_dict(head_only = True))
        self.response.out.write(serialize(testbed_list))

class TestbedResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, testbed_id):
        
        try:
            testbed = Testbed.get_by_id(int(testbed_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(serialize(testbed.to_dict()))
        
# PLATFORM
            
class PlatformCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        resource_list = list()
        query = Platform.all()
        for resource in query:
            resource_list.append(resource.to_dict(head_only = True))
        self.response.out.write(serialize(resource_list))
                
class PlatformResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, resource_id):
        
        try:
            resource = Platform.get_by_key_name(resource_id)
            self.response.out.write(serialize(resource.to_dict()))      
        except:
            self.response.status = '404'

# PROJECT

class ProjectCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        project_list = list()
        
        try:
            query = Project.all().filter('owner =', self.user)
        except:
            query = Project.all()
            
        for project in query:
            project_list.append(project.to_dict(head_only = True))
        self.response.out.write(serialize(project_list))
            
    def post(self):
        
        project_dict = json.loads(self.request.body)
        project = Project()
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.owner = self.user
        project.put()
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % project.uri()
        self.response.headers['Content-Location'] = '%s' % project.uri()
            
class ProjectResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, project_id=None):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, project_id):
        
        try:
            project = Project.get_by_id(int(project_id))            
        except:
            self.response.status = '404'
            
        self.response.out.write(serialize(project.to_dict()))
                
    def put(self, project_id):
        
        project_dict = json.loads(self.request.body)
        
        try:
            project = Project.get_by_id(int(project_id))
        except:
            self.response.status = '404'
            
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.put()
        self.response.out.write(serialize(project.to_dict()))
            
        
            
    def delete(self, project_id):
        
        try:
            project = Project.get_by_id(int(project_id))
        except:
            self.response.status = '404'
        
        project.delete()
        
        
# EXPERIMENT

class ExperimentCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        experiment_list = list()
        
        try:
            query = Experiment.all().filter('owner =', self.user)
        except:
            query = Experiment.all()
            
        for experiment in query:
            experiment_list.append(experiment.to_dict(head_only = True))
        self.response.out.write(serialize(experiment_list))
            
    def post(self):
        
        experiment_dict = json.loads(self.request.body)
        
        experiment = Experiment()
        
        experiment.name = experiment_dict['name']
        experiment.description = experiment_dict['description']
        experiment.owner = self.user
        experiment.project = Project.get_by_id(int(experiment_dict['project_id']))
        experiment.put()
        
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % experiment.uri()
        self.response.headers['Content-Location'] = '%s' % experiment.uri()
            
class ExperimentResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(serialize(experiment.to_dict()))
        
    def put(self, experiment_id):
        
        experiment_dict = json.loads(self.request.body)
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        except:
            self.response.status = '404'

        experiment.name = experiment_dict['name']
        experiment.description = experiment_dict['description']
        experiment.project = Project.get_by_id(int(experiment_dict['project']))
        experiment.put()
        
        self.response.out.write(serialize(experiment.to_dict()))
        
        
    def delete(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        except:
            self.response.status = '404'
            
        experiment.delete()
        

# IMAGE

class ImageCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        experiment = Experiment.get_by_id(int(experiment_id))
        
        image_list = list()
        query = Image.all().filter('experiment =', experiment)
        for image in query:
            image_list.append(image.to_dict(head_only = True))
        self.response.out.write(serialize(image_list))
        
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))

            image_dict = json.loads(self.request.body)

            image = Image()
            image.name = image_dict['name']
            image.description = image_dict['description']
            image.owner = self.user
            image.experiment = experiment
            image.put()

            self.response.status = '201'
            self.response.headers['Location'] = '%s' % image.uri()
            self.response.headers['Content-Location'] = '%s' % image.uri()
            
        except:
            self.response.status = '404'

class ImageResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            self.response.out.write(serialize(image.to_dict()))
        
        except:
            self.response.status = '404'
                
    def put(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            image_dict = json.loads(self.request.body)
            image.name = image_dict['name']
            image.description = image_dict['description']
            image.put()
            self.response.out.write(serialize(image.to_dict()))
            
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            image.delete()
            
        except:
            self.response.status = '404'

class ImageUploadHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, image_id):
        allowed_methods = ['POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def post(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            imagefile = self.request.get('imagefile')
            image.imagefile = imagefile
            image.put()
            self.response.out.write(serialize(image.to_dict()))
            
        except:
            self.response.status = '404'

class ImageDownloadHandler(OAuth2RESTJSONHandler):

    def options(self, experiment_id, image_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            self.response.headers['Content-Type'] = 'application/octet-stream'
            self.response.out.write(image.imagefile)
        
        except:
            self.response.status = '404'

# PROPERTY SET

class PropertySetCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
            property_set_list = list()
            query = PropertySet.all().filter('experiment =', experiment)
            for property_set in query:
                property_set_list.append(property_set.to_dict(head_only = True))
            self.response.out.write(serialize(property_set_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            property_set_dict = json.loads(self.request.body)
        
            platform = Platform.get_by_id(int(property_set_dict['platform_id']))
        
            property_set = PropertySet()
            property_set.name = property_set_dict['name']
            property_set.description = property_set_dict['description']
            property_set.owner = self.user
            property_set.experiment = experiment
            property_set.platform = platform
            property_set.num_nodes = property_set_dict['num_nodes']
            property_set.put()
        
            # now generate virtual nodes!
            
            # generate a list of virtual nodes
            
            vn_list = list()
        
            for k in range(1, property_set.num_nodes + 1):
                vn = VirtualNode()
                vn.name = 'virtual node #%s' % k
                vn.experiment = property_set.experiment
                vn.platform = property_set.platform
                vn.property_set = property_set
                vn.owner = self.user
                # vn.put()
                vn_list.append(vn)
                
            db.put(vn_list)
            
            self.response.status = '201'
            self.response.headers['Location'] = '%s' % property_set.uri()
            self.response.headers['Content-Location'] = '%s' % property_set.uri()
            
        except:
            self.response.status = '404'
            
class PropertySetResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, property_set_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, property_set_id):
        
        try:
            property_set = PropertySet.get_by_id(int(property_set_id))
            self.response.out.write(serialize(property_set.to_dict()))
        
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, property_set_id):
        
        try:
            property_set = PropertySet.get_by_id(int(property_set_id))
            property_set.delete()
            
        except:
            self.response.status = '404'
        
# VIRTUAL NODE
        
class VirtualNodeCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_node_list = list()
            query = VirtualNode.all().filter('experiment =', experiment)
            for virtual_node in query:
                virtual_node_list.append(virtual_node.to_dict(head_only = True))
            self.response.out.write(serialize(virtual_node_list))
            
        except:
            self.response.status = '404'

class VirtualNodeResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, virtual_node_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, virtual_node_id):
        
        try:
            virtual_node = VirtualNode.get_by_id(int(virtual_node_id))
            self.response.out.write(serialize(virtual_node.to_dict()))
            
        except:
            self.response.status = '404'
        
# VIRTUAL NODE GROUP

class VirtualNodeGroupCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_nodegroup_list = list()
            query = VirtualNodeGroup.all().filter('experiment =', experiment)
            for virtual_nodegroup in query:
                virtual_nodegroup_list.append(virtual_nodegroup.to_dict(head_only = True))
            self.response.out.write(serialize(virtual_nodegroup_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            vng_dict = json.loads(self.request.body)
        
            vng = VirtualNodeGroup()
            vng.name = vng_dict['name']
            vng.description = vng_dict['description']
            vng.owner = self.user
            vng.experiment = experiment
            vng.put()

            for vn_id in vng_dict['virtual_nodes']:
                VirtualNodeGroup2VirtualNode(vng = vng, vn = VirtualNode.get_by_id(int(vn_id))).put()
        
            self.response.status = '201'
            self.response.headers['Location'] = '%s' % vng.uri()
            self.response.headers['Content-Location'] = '%s' % vng.uri()
            
        except:
            self.response.status = '404'

class VirtualNodeGroupResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, virtual_nodegroup_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, virtual_nodegroup_id):
        
        try:
            virtual_nodegroup = VirtualNodeGroup.get_by_id(int(virtual_nodegroup_id))
            self.response.out.write(serialize(virtual_nodegroup.to_dict()))
            
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, virtual_nodegroup_id):
        
        try:
            virtual_nodegroup = VirtualNodeGroup.get_by_id(int(virtual_nodegroup_id))
            virtual_nodegroup.delete()
            
        except:
            self.response.status = '404'
    
# VIRTUAL TASK

class VirtualTaskCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_task_list = list()
            query = VirtualTask.all().filter('experiment =', experiment)
            for virtual_task in query:
                virtual_task_list.append(virtual_task.to_dict(head_only = True))
            self.response.out.write(serialize(virtual_task_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
            
            vt_dict = json.loads(self.request.body)

            vt = VirtualTask()
            vt.name = vt_dict['name']
            vt.description = vt_dict['description']
            vt.method = vt_dict['method']
            vt.target = vt_dict['target']
            vt.owner = self.user
            vt.experiment = experiment
            vt.put()

            self.response.status = '201'
            self.response.headers['Location'] = '%s' % vt.uri()
            self.response.headers['Content-Location'] = '%s' % vt.uri()
            
        except:
            self.response.status = '404'

class VirtualTaskResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, vt_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, vt_id):
        
        try:
            vt = VirtualTask.get_by_id(int(vt_id))
            self.response.out.write(serialize(vt.to_dict()))
        
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, vt_id):
        
        try:
            vt = VirtualTask.get_by_id(int(vt_id))
            vt.delete()
        
        except:
            self.response.status = '404'
    
# JOB

class JobCollectionHandler(OAuth2RESTJSONHandler):
    pass

class JobResourceHandler(OAuth2RESTJSONHandler):
    pass