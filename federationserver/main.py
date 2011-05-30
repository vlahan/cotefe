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
        
        (r'^/token', OpenIdTokenHandler)
        
        (r'^/$', FederationHandler),
        
        (r'^/testbeds/$',                       TestbedHandler),
        (r'^/testbeds/(.*)/(.*)/$',             TestbedHandler),
        (r'^/testbeds/(.*)$',                   TestbedHandler),
        
        (r'^/jobs/$',                           JobHandler),
        (r'^/jobs/(.*)$',                       JobHandler),
        
        (r'^/platforms/$',                      PlatformHandler),
        (r'^/platforms/(.*)$',                  PlatformHandler),
        
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()