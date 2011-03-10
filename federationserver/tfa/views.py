import xmlrpclib

from datetime import datetime
# import base64
# import hashlib
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from testbedserver.taa.models import *
from django.contrib.auth.models import User
from testbedserver.utils.odict import OrderedDict

TAA_PROTOCOL = 'http'
TAA_HOST = 'localhost'
TAA_PORT = '8001'

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True
JSON_SORT_KEYS = False

# XML PROXY CONFIGURATION
XMLRPC_PROTOCOL = 'https'
XMLRPC_HOST = '127.0.0.1'
XMLRPC_PORT = '8005'
XMLRPC_USERNAME = 'conetuser'
XMLRPC_PASSWORD = 'password'

tn_server = xmlrpclib.ServerProxy(
    '%s://%s:%s@%s:%s' % (
        XMLRPC_PROTOCOL,
        XMLRPC_USERNAME,
        XMLRPC_PASSWORD,
        XMLRPC_HOST,
        XMLRPC_PORT
    )
)


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