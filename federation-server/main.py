import logging
from django.utils import simplejson as json
from odict import OrderedDict

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

# DATASTORE MODEL

class Federation(db.Model):
    uri = db.StringProperty()
    media_type = db.StringProperty()
    name = db.StringProperty()
    # testbeds = db.ListProperty()
    # jobs = db.ListProperty()
    
class Testbed(db.Model):
    uri = db.StringProperty()
    media_type = db.StringProperty()
    name = db.StringProperty()
    organiziation = db.StringProperty()
    server_url = db.StringProperty()
    
class Platform(db.Model):
    uri = db.StringProperty()
    media_type = db.StringProperty()
    name = db.StringProperty()
    
class Job(db.Model):
    name = db.StringProperty()
    uri = db.StringProperty()
    media_type = db.StringProperty()
    # testbed = db.ReferenceProperty(Testbed)
    datetime_from = db.DateTimeProperty()
    datetime_to   = db.DateTimeProperty()


# TASK EXAMPLE

class TasksHandler(webapp.RequestHandler):
    def post(self):
        taskqueue.add(
            method = 'POST',
            url = '/reflector',
            params = {
                'method' : 'PUT',
                'url' : 'http://127.0.0.1:8081/nodegroups/123',
            }
        )
        self.response.set_status(201)
        self.response.out.write('New Task created at <a href="http://localhost:8080/tasks/456">http://localhost:8080/tasks/456</a>\n')
    
class TaskHandler(webapp.RequestHandler):
    def get(self):
        self.response.set_status(200)
        self.response.out.write('Task ID = 456, Method = PUT, URL = http://localhost:8000/nodegroups/123\n')

class Reflector(webapp.RequestHandler):
    def post(self):
        # logging.info(self.request.get('method'))
        # logging.info(self.request.get('url'))
        result = urlfetch.fetch(
            method = self.request.get('method'),
            url = self.request.get('url'),
        )
    
# CONET DEMO

class FederationResourceHandler(webapp.RequestHandler):
    def get(self):
        federation_dict = OrderedDict()
        federation_dict['uri'] = "https://conet-testbed-federation.appspot.com/"
        federation_dict['media_type'] = "application/json"
        federation_dict['name'] = "CONET Testbed Federation"
        federation_dict['testbeds'] = "https://conet-testbed-federation.appspot.com/testbeds/"
        federation_dict['jobs'] = "https://conet-testbed-federation.appspot.com/jobs/"
        
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json.dumps(federation_dict))
        
class TestbedCollectionHandler(webapp.RequestHandler):
    def get(self):
        pass
        # self.response.out.write(json.dumps(testbeds))
        
    
class JobCollectionHandler(webapp.RequestHandler):
    def get(self):
        result = urlfetch.fetch(
            method = 'GET',
            url = 'http://127.0.0.1:8000/jobs/',
        )
        self.response.set_status(200)
        self.response.out.write(result.content)
            
def main():
    application = webapp.WSGIApplication([
        # ('/tasks/', TasksHandler),
        # ('/tasks/456', TaskHandler),
        # ('/reflector', Reflector),

        ('/',                 FederationResourceHandler)
        # ('/testbeds/',        TestbedCollectionHandler)
        # ('/testbeds/(.*)',    TestbedResourceHandler)
        # ('/jobs/',            JobCollectionHandler)
        # ('/jobs/(.*)',        JobResourceHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
