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
from google.appengine.ext import db

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
        for federation in Federation.all(): federation.delete()
        for testbed in Testbed.all(): testbed.delete()
        for platform in Platform.all(): platform.delete()
        for project in Project.all(): project.delete()
        for experiment in Experiment.all(): experiment.delete()
        
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
                'server_url' : self.request.host_url,
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
            
            applications = Application.all().filter('owner =', user).fetch(100)
            
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
        
class Docs(BaseHandler):

    def get(self):

        try:
            user = User.all().filter('username =', self.session.get('username')).fetch(1)[0]
            context = {
                'user': user,
            }
        except:
            context = {}
        
        self.render_response('docs.html', **context)        
        
class Users(BaseHandler):

    def get(self):

        if self.session.get('username'):

            username = self.session.get('username')
            user = User.all().filter('username =', username).fetch(1)[0]

            users = User.all()
            
            context = {
                'user': user,
                'users': users,
            }
            self.render_response('explore/users.html', **context)
            
        else:
            
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
    def post(self):

        if self.session.get('username'):
            
            user_id = self.request.get('user_id')
            User.get_by_id(int(user_id)).delete()
            self.redirect(self.request.referer)
            
        else:
            
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
        
        
class Testbeds(BaseHandler):

    def get(self):

        if self.session.get('username'):
            
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            
            testbeds = Testbed.all()
            context = {
                'user': user,
                'testbeds': testbeds,
            }
            self.render_response('explore/testbeds.html', **context)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))

            
class Platforms(BaseHandler):

    def get(self):

        if self.session.get('username'):

            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]

            platforms = Platform.all()
            context = {
                'user': user,
                'platforms': platforms,
            }
            self.render_response('explore/platforms.html', **context)
        else:
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Projects(BaseHandler):

    def get(self):

        if self.session.get('username'):
            
            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]
            
            projects = Project.all().filter('owner =', user).fetch(100)
            
            context = {
                'user': user,
                'projects': projects,
            }
            self.render_response('cotefe/projects.html', **context)
        
        else:
            
            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))

    def post(self):

        if self.session.get('username'):

            if self.request.get('submit') == 'Create':

                username = self.session.get('username')
                user_list = User.all().filter('username =', username).fetch(1)
                user = user_list[0]

                name = self.request.get('name')
                description = self.request.get('description')

                project = Project()
                project.name = name
                project.description = description
                project.owner = user
                project.put()

                self.redirect(self.request.referer)

            elif self.request.get('submit') == 'Delete':
                
                project_id = self.request.get('project_id')
                
                def delete_project(project_id):
                    
                    project = Project.get_by_id(int(project_id))
                    project.delete()
                    
                    for experiment in Experiment.all().filter('project =', project):
                        experiment.delete()
                        
                # db.run_in_transaction(delete_project, project_id)
                
                delete_project(project_id)
                
                self.redirect(self.request.referer)

        else:

            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))
            
class Experiments(BaseHandler):

    def get(self):

        if self.session.get('username'):

            username = self.session.get('username')
            user_list = User.all().filter('username =', username).fetch(1)
            user = user_list[0]

            projects = Project.all().filter('owner =', user).fetch(100)
            experiments = Experiment.all().filter('owner =', user).fetch(100)

            context = {
                'user': user,
                'projects': projects,
                'experiments': experiments,
            }
            self.render_response('cotefe/experiments.html', **context)

        else:

            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))

    def post(self):

        if self.session.get('username'):

            if self.request.get('submit') == 'Create':

                username = self.session.get('username')
                user = User.all().filter('username =', username).fetch(1)[0]
                
                project_id = self.request.get('project_id')
                project = Project.get_by_id(int(project_id))

                name = self.request.get('name')
                description = self.request.get('description')

                experiment = Experiment()
                experiment.name = name
                experiment.description = description
                experiment.project = project
                experiment.owner = user
                experiment.put()

                self.redirect(self.request.referer)

            elif self.request.get('submit') == 'Delete':

                experiment_id = self.request.get('experiment_id')
                Experiment.get_by_id(int(experiment_id)).delete()

                self.redirect(self.request.referer)

        else:

            params = {
                'next': '%s%s' % (config.FEDERATION_SERVER_URL, self.request.path),
            }
            self.redirect('%s?%s' % ('/openid/login', urllib.urlencode(params)))


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
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self):
        
        self.response.out.write(serialize(self.user.to_dict()))        
        
        
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
        
        user = User.get_by_id(int(user_id))
        self.response.out.write(serialize(user.to_dict()))
        
# FEDERATION
            
class FederationResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
            
        federation = Federation.all().get()
        self.response.out.write(serialize(federation.to_dict()))
            
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
        
        testbed = Testbed.get_by_id(int(testbed_id))
        self.response.out.write(serialize(testbed.to_dict()))
        
# PLATFORM
            
class PlatformCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        platform_list = list()
        query = Platform.all()
        if self.request.get('name'):
            query = query.filter('name =', self.request.get('name'))
        for platform in query:
            platform_list.append(platform.to_dict(head_only = True))
        self.response.out.write(serialize(platform_list))
                
class PlatformResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, platform_id):
        
        platform = Platform.get_by_id(int(platform_id))
        self.response.out.write(serialize(platform.to_dict()))

# PROJECT

class ProjectCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        project_list = list()
        for project in Project.all().filter('owner =', self.user):
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
        self.response.headers['Location'] = '%s' % (project.uri())
        self.response.headers['Content-Location'] = '%s' % (project.uri())
            
class ProjectResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
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
        
# EXPERIMENT

class ExperimentCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        experiment_list = list()
        for experiment in Experiment.all().filter('owner =', self.user):
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
        self.response.headers['Location'] = '%s' % (experiment.uri())
        self.response.headers['Content-Location'] = '%s' % (experiment.uri())
            
class ExperimentResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        experiment = Experiment.get_by_id(int(experiment_id))
        self.response.out.write(serialize(experiment.to_dict()))
                
    def put(self, experiment_id):
        
        experiment_dict = json.loads(self.request.body)
        experiment = Experiment.get_by_id(int(experiment_id))
        experiment.name = experiment_dict['name']
        experiment.description = experiment_dict['description']
        experiment.project = Project.get_by_id(int(experiment_dict['project']))
        experiment.put()
        self.response.out.write(serialize(experiment.to_dict()))
            
    def delete(self, experiment_id):
        
        experiment = Experiment.get_by_id(int(experiment_id))
        experiment.delete()
        self.response.status = '204'