import os
import logging
from django.utils import simplejson as json
import uuid
import hashlib

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

from models import *
from config import *

class DatastoreInitialization(webapp.RequestHandler):

    def get(self):
        for f in FederationResource.all(): f.delete()
        f1 = FederationResource()
        f1.name = 'CONET Testbed Federation'
        f1.put()
        
        for t in TestbedResource.all(): t.delete()
        t1 = TestbedResource()
        t1.protocol = TAA_PROTOCOL
        t1.host = TAA_HOST
        t1.port = TAA_PORT
        t1.put()
        
        for j in JobResource.all(): j.delete()
        
        self.response.out.write('Datastore has been initialized!')
        
class AuthorizationEndpoint(webapp.RequestHandler):
    
    def get(self):
        client_id = self.request.get('client_id')
        response_type = self.request.get('response_type')
        callback_uri = self.request.get('callback_uri')
        
        # se c'e' almeno un application con client_id:
            # creo una session con quel client_id
            # se response_type = 'code'
                # setto oauth_response_type = 'code'
                # renderizzo il login_form con parametri nascosti
                # template_values = { 'oauth_session' : oauth_session }

class LoginEndpoint(webapp.RequestHandler):
    
    def post(self):
        client_id = self.request.get('client_id')
        response_type = self.request.get('response_type')
        callback_uri = self.request.get('callback_uri')
        username = self.request.get('username')
        password = self.request.get('password')
        #  se il login va a buon fine
            # oauth_session.oauth_code = uuid.uuid4().hex
            # oauth_session.put()
            # self.redirect(callback_uri + 'code=' + oauth_session.oauth_code)
        

class TokenEndpoint(webapp.RequestHandler):
    
    def post(self):
        client_id = self.request.get('client_id')
        callback_uri = self.request.get('callback_uri')
        code = self.request.get('code')
        grant_type = self.request('grant_type')
        
        # se usiste la session per questi dati
            # oauth_session.oauth_access_token = uuid.uuid4().hex
            # oauth_session.put()
            # setto l'header a application/json
            # invio il dizionario contente l'access token
            
class ApplicationManager(webapp.RequestHandler):
    
    def get(self):
        apps = Application.all()
        template_values = { 'apps' : apps }
        path = os.path.join(os.path.dirname(__file__), 'templates/apps.html')
        logging.info(path)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        app = Application()
        app.name = self.request.get('name')
        app.oauth_callback_url = self.request.get('oauth_callback_url')
        app.oauth_client_id = uuid.uuid4().hex
        app.oauth_client_secret = uuid.uuid4().hex
        app.put()
        self.redirect('/apps')

class UserManager(webapp.RequestHandler):
    
    def get(self):
        apps = User.all()
        template_values = { 'users' : apps }
        path = os.path.join(os.path.dirname(__file__), 'templates/users.html')
        logging.info(path)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        user = User()
        user.first_name = self.request.get('first_name')
        user.last_name = self.request.get('last_name')
        user.username = self.request.get('username')
        m = hashlib.md5()
        m.update(self.request.get('password'))
        user.password_hash = m.hexdigest()
        user.email = self.request.get('email')
        user.openid = self.request.get('openid')
        user.put()
        self.redirect('/users')
        
class FederationHandler(webapp.RequestHandler):
    def get(self):
        federation = FederationResource.all().get()
        if federation:
            self.response.out.write(json.dumps(federation.to_dict()))
        else:
            self.error(404)
        
class TestbedHandler(webapp.RequestHandler):
    def get(self, res_id = None, sub_res = None):
        # logging.info("res_id = %s", res_id)
        # logging.info("sub_res = %s", sub_res)
        
        # /testbeds/
        if res_id == None:
            # UPDATES INFORMATION ABOUT TESTBEDS AND SAVES TO DATASTORE
            for testbed in TestbedResource.all():
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
            for testbed in TestbedResource.all():
                testbed_list.append(testbed.to_dict(head_only = True))
            # SENDS BACK THE JSON DUMP OF THE LIST
            self.response.out.write(json.dumps(testbed_list))
        else:
            testbed = TestbedResource.get_by_id(int(res_id))
            
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
            for testbed in TestbedResource.all():
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
                    platform = PlatformResource()
                    platform.name = platform_dict['name']
                    platform.tinyos_name = platform_dict['tinyos_name']
                    platform.put()

                # NOW RETRIEVE ALL THE JOBS FROM THE DATASTORE
                platform_list = list()
                for platform in PlatformResource.all():
                    platform_list.append(platform.to_dict(head_only = True))
            self.response.out.write(json.dumps(platform_list))

        # /jobs/ID
        else:
            platform = PlatformResource.get_by_id(int(res_id))
            self.response.out.write(json.dumps(platform.to_dict()))


class JobHandler(webapp.RequestHandler):
    def get(self, res_id = None):
        # logging.info("res_id = %s", res_id)
        
        # /jobs/
        if res_id == None:
            # FOR EVERY TESTBED
            for testbed in TestbedResource.all():
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
                    job = JobResource()
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
                for job in JobResource.all():
                    job_list.append(job.to_dict(head_only = True))
            self.response.out.write(json.dumps(job_list))
        
        # /jobs/ID
        else:
            job = JobResource.get_by_id(int(res_id))
            self.response.out.write(json.dumps(job.to_dict()))