import logging
from django.utils import simplejson as json
from odict import OrderedDict

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

# INFORMATION FOR BUILDING URLS
FS_PROTOCOL = 'http'
# FS_HOST = 'federation-server.appspot.com'
FS_HOST = 'localhost'
FS_PORT = '8080'

# TESTBED SERVER CONFIGURATION
TS_PROTOCOL = 'http'
# TS_HOST = 'www.twist.tu-berlin.de'
TS_HOST = 'localhost'
TS_PORT = '8001'

# UTILITY FUNCTIONS

def build_url(protocol = 'http', host = 'localhost', port = '80', path = '/'):
    return protocol + '://' + host + ':' + port + path

# DATASTORE MODELS

class Federation(db.Model):
    name = db.StringProperty()
    
    def to_dict(self, head_only = False):
        federation = OrderedDict()
        federation['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT)
        federation['media_type'] = 'application/json'
        federation['name'] = self.name
        federation['testbeds'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/')
        federation['platforms'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/')
        federation['jobs'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/jobs/')
        return federation
    
class Testbed(db.Model):
    # STATIC INFORMATION (INSERTED BY ADMIN)
    protocol = db.StringProperty()
    host = db.StringProperty()
    port = db.StringProperty()
    
    # DYNAMIC FIELDS, RETRIEVED BY HTTP GET ON TESTBED URL
    name = db.StringProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        testbed = OrderedDict()
        testbed['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/' + str(self.key().id()))
        testbed['media_type'] = 'application/json'
        testbed['name'] = self.name
        if not head_only:
            testbed['organization'] = self.organization
            testbed['platforms'] = testbed['uri'] + '/platforms/'
            testbed['jobs'] = testbed['uri'] + '/jobs/'
        return testbed

class Platform(db.Model):
    name = db.StringProperty()
    tinyos_name = db.StringProperty()
    
    def to_dict(self, head_only = False):
        platform = OrderedDict()
        platform['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/' + str(self.key().id()))
        platform['media_type'] = 'application/json'
        platform['name'] = self.name
        if not head_only:
            platform['tiny_os'] = self.tinyos_name
        return platform
    
class Job(db.Model):
    name = db.StringProperty()
    testbed = db.ReferenceProperty(Testbed)
    datetime_from = db.StringProperty()
    datetime_to = db.StringProperty()
    uid = db.StringProperty()
    
    def to_dict(self, head_only = False):
        job = OrderedDict()
        job['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/jobs/' + str(self.key().id()))
        job['media_type'] = 'application/json'
        job['name'] = self.name
        if not head_only:
            job['testbed'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/' + str(self.testbed.key().id()))
            job['datetime_from'] = self.datetime_from
            job['datetime_to'] = self.datetime_to
            job['uid'] = self.uid
        return job
        
    
# DATASTORE INITIALIZATION
    
class DatastoreInitialization(webapp.RequestHandler):
    def get(self):
        
        # INITIALIZE FEDERATION DATASTORE
        for f in Federation.all(): f.delete()

        f1 = Federation()
        f1.name = 'CONET Testbed Federation'
        f1.put()
        
        # INITIALIZE TESTBED DATASTORE
        for t in Testbed.all(): t.delete()

        t1 = Testbed()
        t1.protocol = TS_PROTOCOL
        t1.host = TS_HOST
        t1.port = TS_PORT
        t1.put()
        
        # INITIALIZE JOB DATASTORE
        for j in Job.all(): j.delete()
        
        
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

class FederationHandler(webapp.RequestHandler):
    def get(self):
        federation = Federation.all().get()
        self.response.out.write(json.dumps(federation.to_dict()))
        
class TestbedHandler(webapp.RequestHandler):
    def get(self, res_id = None, sub_res = None):
        # logging.info("res_id = %s", res_id)
        # logging.info("sub_res = %s", sub_res)
        
        # /testbeds/
        if res_id == None:
            # UPDATES INFORMATION ABOUT TESTBEDS AND SAVES TO DATASTORE
            for testbed in Testbed.all():
                result = urlfetch.fetch(
                    method = 'GET',
                    url = build_url(testbed.protocol, testbed.host, testbed.port),
                    validate_certificate = False
                )
                testbed_dict = json.loads(result.content)
                testbed.name = testbed_dict['name']
                testbed.organization = testbed_dict['organization']
                testbed.put()
            # RETRIEVES THE LIST OF TESTBEDS FROM THE DATASORE
            testbed_list = list()
            for testbed in Testbed.all():
                testbed_list.append(testbed.to_dict(head_only = True))
            # SENDS BACK THE JSON DUMP OF THE LIST
            self.response.out.write(json.dumps(testbed_list))
        else:
            testbed = Testbed.get_by_id(int(res_id))
            
            # /testbeds/ID
            if sub_res == None:
                result = urlfetch.fetch(
                    method = 'GET',
                    url = build_url(testbed.protocol, testbed.host, testbed.port),
                    validate_certificate = False
                )
                testbed_dict = json.loads(result.content)
                testbed.name = testbed_dict['name']
                testbed.organization = testbed_dict['organization']
                testbed.put()
                self.response.out.write(json.dumps(testbed.to_dict()))
            
            # /testbeds/ID/sub_res
            else:
                result = urlfetch.fetch(
                    method = 'GET',
                    url = build_url(testbed.protocol, testbed.host, testbed.port, '/' + sub_res + '/'),
                    validate_certificate = False
                )
                self.response.out.write(result.content)
                
class PlatformHandler(webapp.RequestHandler):
    def get(self, res_id = None):
        # logging.info("res_id = %s", res_id)

        # /platforms/
        if res_id == None:
            # FOR EVERY TESTBED
            for testbed in Testbed.all():
                # GET ALL PLATFORMS
                result = urlfetch.fetch(
                    method = 'GET',
                    url = build_url(testbed.protocol, testbed.host, testbed.port, '/platforms/'),
                    validate_certificate = False
                )
                # BUILD A LIST OF PLATFORMS
                platform_list = json.loads(result.content)
                # FOR EVERY PLATFORM IN THE LIST
                for platform_dict in platform_list:
                    # GET THE PLATFORM
                    result = urlfetch.fetch(
                        method = 'GET',
                        url = platform_dict['uri'],
                        validate_certificate = False
                    )
                    platform_dict = json.loads(result.content)
                    
                    logging.info("platform_dict = %s", platform_dict)
                    
                    # CREATE ADN SAVE A PLATFORM MODEL WITHE THE FOLLOWING FIELDS
                    # UNICITY CHECK MISSING HERE!
                    platform = Platform()
                    platform.name = platform_dict['name']
                    platform.tinyos_name = platform_dict['tinyos_name']
                    platform.put()

                # NOW RETRIEVE ALL THE JOBS FROM THE DATASTORE
                platform_list = list()
                for platform in Platform.all():
                    platform_list.append(platform.to_dict(head_only = True))
            self.response.out.write(json.dumps(platform_list))

        # /jobs/ID
        else:
            platform = Platform.get_by_id(int(res_id))
            self.response.out.write(json.dumps(platform.to_dict()))


class JobHandler(webapp.RequestHandler):
    def get(self, res_id = None):
        # logging.info("res_id = %s", res_id)
        
        # /jobs/
        if res_id == None:
            # FOR EVERY TESTBED
            for testbed in Testbed.all():
                # GET ALL JOBS
                result = urlfetch.fetch(
                    method = 'GET',
                    url = build_url(testbed.protocol, testbed.host, testbed.port, '/jobs/'),
                    validate_certificate = False
                )
                # BUILD A LIST OF JOBS
                job_list = json.loads(result.content)
                # FOR EVERY JOB IN THE LIST
                for job_dict in job_list:
                    # GET THE JOB
                    result = urlfetch.fetch(
                        method = 'GET',
                        url = job_dict['uri'],
                        validate_certificate = False
                    )
                    job_dict = json.loads(result.content)
                    # CREATE AND SAVE A JOB MODEL WITH THE FOLLOWING FIELDS
                    # UNICITY CHECK MISSING HERE!
                    job = Job()
                    job.name = job_dict['name']
                    job.testbed = testbed
                    job.datetime_from = job_dict['datetime_from']
                    job.datetime_to = job_dict['datetime_to']
                    # GENERATES A UNIQUE ID FROM THE URI
                    m = hashlib.md5()
                    m.update(job_dict['uri'])
                    job.uid = m.hexdigest()
                    job.put()
                
                # NOW RETRIEVE ALL THE JOBS FROM THE DATASTORE
                job_list = list()
                for job in Job.all():
                    job_list.append(job.to_dict(head_only = True))
            self.response.out.write(json.dumps(job_list))
        
        # /jobs/ID
        else:
            job = Job.get_by_id(int(res_id))
            self.response.out.write(json.dumps(job.to_dict()))
    
def main():
    
    application = webapp.WSGIApplication([
        # ('/tasks/', TasksHandler),
        # ('/tasks/456', TaskHandler),
        # ('/reflector', Reflector),
        
        (r'^/$', FederationHandler),
        
        (r'^/testbeds/$', TestbedHandler),
        (r'^/testbeds/(.*)/(.*)/$', TestbedHandler),
        (r'^/testbeds/(.*)$', TestbedHandler),
        
        (r'^/jobs/$', JobHandler),
        (r'^/jobs/(.*)$', JobHandler),
        
        (r'^/platforms/$', PlatformHandler),
        (r'^/platforms/(.*)$', PlatformHandler),
        
        (r'^/datastore-initialization$', DatastoreInitialization),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
