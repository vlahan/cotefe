from google.appengine.dist import use_library
use_library('django', '1.2')

import logging
from django.utils import simplejson as json
from odict import OrderedDict

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from models import *
from handlers import *
from openid import *

def main():
    
    application = webapp.WSGIApplication([
        # ('/tasks/', TasksHandler),
        # ('/tasks/456', TaskHandler),
        # ('/reflector', Reflector),
        
        (r'^/init$', DatastoreInitialization),
        
        (r'^/apps$', ApplicationManager),
        (r'^/users$', UserManager),
        
        (r'^/auth$', AuthorizationEndpoint),
        (r'^/login$', LoginEndpoint),
        (r'^/token$', TokenEndpoint),
        
        (r'^/api/$', FederationHandler),
        
        (r'^/api/testbeds/$', TestbedHandler),
        (r'^/api/testbeds/(.*)/(.*)/$', TestbedHandler),
        (r'^/api/testbeds/(.*)$', TestbedHandler),
        
        (r'^/api/jobs/$', JobHandler),
        (r'^/api/jobs/(.*)$', JobHandler),
        
        (r'^/api/platforms/$', PlatformHandler),
        (r'^/api/platforms/(.*)$', PlatformHandler),
        
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()