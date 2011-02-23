import logging
import re
from django.utils import simplejson as json
from odict import OrderedDict

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

# DATASTORE MODEL

# class Federation(db.Model):
#     uri = db.StringProperty()
#     media_type = db.StringProperty()
#     name = db.StringProperty()
#     # testbeds = db.ListProperty()
#     # jobs = db.ListProperty()
    
class Testbed(db.Model):
    name = db.StringProperty()
    organization = db.StringProperty()
    server_url = db.StringProperty()
    
    def to_dict(self, head_only = False):
        testbed = OrderedDict()
        testbed['uri'] = 'https://federation-server.appspot.com/testbeds/' + str(self.key().id())
        testbed['media_type'] = 'application/json'
        testbed['name'] = self.name
        if not head_only:
            testbed['organization'] = self.organization
            testbed['server_url'] = self.server_url + '/'
            # testbed['platforms'] = testbed['uri'] + '/platforms/'
            # testbed['jobs'] = testbed['uri'] + '/jobs/'
        return testbed
    
# class Platform(db.Model):
#     uri = db.StringProperty()
#     media_type = db.StringProperty()
#     name = db.StringProperty()
    
# class Job(db.Model):
#     name = db.StringProperty()
#     # testbed = db.ReferenceProperty(Testbed)
#     datetime_from = db.DateTimeProperty()
#     datetime_to   = db.DateTimeProperty()
#     
#     def to_dict(self):
#         job = OrderedDict()
#         job['uri'] = 'https://federation-server.appspot.com/jobs/' + str(self.key().id())
#         job['media_type'] = 'application/json'
#         job['name'] = self.name
#         job['organization'] = self.organization
#         job['server_url'] = self.server_url
#         job['platforms'] = job['uri'] + '/platforms/'
#         job['jobs'] = job['uri'] + '/jobs/'
#         return job
        
    
# DATASTORE INITIALIZATION
    
class DatastoreInitialization(webapp.RequestHandler):
    def get(self):
        # initialize Testbed table
        for t in Testbed.all():
            t.delete()

        t1 = Testbed()
        t1.name = 'TWIST'
        t1.organization = 'TU Berlin'
        t1.server_url = 'https://www.twist.tu-berlin.de:8001'
        t1.put()
        
        t2 = Testbed()
        t2.name = 'Other Testbed'
        t2.organization = 'Other Organization'
        t2.server_url = 'https://www.example.org'
        t2.put()
        self.response.out.write('Datastore has been initialized!')


# TASK EXAMPLE

# class TasksHandler(webapp.RequestHandler):
#     def post(self):
#         taskqueue.add(
#             method = 'POST',
#             url = '/reflector',
#             params = {
#                 'method' : 'PUT',
#                 'url' : 'http://127.0.0.1:8081/nodegroups/123',
#             }
#         )
#         self.response.set_status(201)
#         self.response.out.write('New Task created at <a href="http://localhost:8080/tasks/456">http://localhost:8080/tasks/456</a>\n')
#     
# class TaskHandler(webapp.RequestHandler):
#     def get(self):
#         self.response.set_status(200)
#         self.response.out.write('Task ID = 456, Method = PUT, URL = http://localhost:8000/nodegroups/123\n')
# 
# class Reflector(webapp.RequestHandler):
#     def post(self):
#         # logging.info(self.request.get('method'))
#         # logging.info(self.request.get('url'))
#         result = urlfetch.fetch(
#             method = self.request.get('method'),
#             url = self.request.get('url'),
#         )
    
# CONET DEMO

class FederationResourceHandler(webapp.RequestHandler):
    def get(self):
        federation_dict = OrderedDict()
        federation_dict['uri'] = "https://federation-server.appspot.com/"
        federation_dict['media_type'] = "application/json"
        federation_dict['name'] = "CONET Federation Server"
        federation_dict['testbeds'] = "https://federation-server.appspot.com/testbeds/"
        federation_dict['jobs'] = "https://federation-server.appspot.com/jobs/"
        
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json.dumps(federation_dict))
        
class TestbedCollectionHandler(webapp.RequestHandler):
    def get(self):
        testbed_collection_list = list()
        for testbed in Testbed.all():
            testbed_collection_list.append(testbed.to_dict(head_only = True))
        self.response.out.write(json.dumps(testbed_collection_list))
        
class TestbedResourceHandler(webapp.RequestHandler):
    def get(self, id):
        testbed = Testbed.get_by_id(int(id))
        self.response.out.write(json.dumps(testbed.to_dict(head_only = False)))

# class JobCollectionHandler(webapp.RequestHandler):
#     def get(self):
#         result = urlfetch.fetch(
#             method = 'GET',
#             url = 'http://127.0.0.1:8000/jobs/',
#             validate_certificate = None
#         )
#         self.response.set_status(200)
#         self.response.out.write(result.content)
        
class TestbedJobCollectionHandler(webapp.RequestHandler):
    def get(self, id, slug):
        result = urlfetch.fetch(
            method = 'GET',
            url = Testbed.get_by_id(int(id)).server_url + '/jobs/',
            validate_certificate = False
        )
        self.response.set_status(200)
        self.response.out.write(result.content)
            
def main():
    
    application = webapp.WSGIApplication([
        # ('/tasks/', TasksHandler),
        # ('/tasks/456', TaskHandler),
        # ('/reflector', Reflector),
        
        (r'^/$', FederationResourceHandler),
        (r'^/testbeds/$', TestbedCollectionHandler),

        (r'^/testbeds/(.*)/(.*)/$', TestbedJobCollectionHandler),
        (r'^/testbeds/(.*)$', TestbedResourceHandler),
        
        
        
        
        
        # (r'/jobs/', JobCollectionHandler),
        # (r'/jobs/(.*)', JobResourceHandler),
        
        (r'^/datastore-initialization/$',   DatastoreInitialization),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
