import webapp2
from webapp2_extras import sessions
from webapp2_extras import jinja2

import config
import utils

from models import OAuth2Session

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
                self.response.out.write(utils.serialize(error))
        else:
            
            if self.request.method == 'GET':
                webapp2.RequestHandler.dispatch(self)
            else:
                error = {
                    'status': 401,
                    'message': "Ah, you need an access_token!"
                }
                self.response.status = '401'
                self.response.out.write(utils.serialize(error))
                