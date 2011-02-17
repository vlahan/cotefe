import xmlrpclib
from datetime import datetime
import base64
import hashlib
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from api.models import Testbed, Platform, Job
from django.contrib.auth.models import User
from odict import OrderedDict

SERVER_ADDR = '127.0.0.1'
SERVER_PORT = '8001'
SERVER_PATH = 'http://' + SERVER_ADDR + ':' + SERVER_PORT
MEDIA_TYPE = 'application/json'

# CONTENT_TYPE = 'application/json;charset=utf-8'
CONTENT_TYPE = 'text/plain'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True
JSON_SORT_KEYS = False

XMLRPC_HOST = '127.0.0.1'
XMLRPC_PORT = '8002'
XMLRPC_USERNAME = 'conetuser'
XMLRPC_PASSWORD = 'password'
s = xmlrpclib.ServerProxy('http://%s:%s@%s:%s/RPC2' % (XMLRPC_USERNAME, XMLRPC_PASSWORD, XMLRPC_HOST, XMLRPC_PORT))

# UTILITY FUNCTIONS

def model_to_string(resource):
    if isinstance(resource, User):
        return 'user'
    elif isinstance(resource, Testbed):
        return 'testbed'
    elif isinstance(resource, Platform):
        return 'platform'
    elif isinstance(resource, Job):
        return 'job'

def resource_model_to_dict(resource_model, head_only=False):
    resource_dict = OrderedDict()
    
    resource_dict['uri'] = SERVER_PATH + resource_model.get_absolute_url()
    resource_dict['media_type'] = MEDIA_TYPE
    
    if isinstance(resource_model, User):
        resource_dict['name'] = resource_model.username
        
    elif isinstance(resource_model, Platform):
        resource_dict['name'] = resource_model.name
        
    if not head_only:
        if isinstance(resource_model, User):
            resource_dict['first_name'] = resource_model.first_name
            resource_dict['last_name'] = resource_model.last_name
            resource_dict['email'] = resource_model.email

    return resource_dict  

#def resource_dict_to_model(resource_dict):
#    resource_model = Image(name = resource_dict['name'])
#    return resource_model
    
def resource_dict_to_json(resource_dict):
    return simplejson.dumps(resource_dict, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT, sort_keys=JSON_SORT_KEYS)

def resource_json_to_dict(resource_json):
    return simplejson.loads(resource_json)

def collection_queryset_to_list(collection_queryset):
    collection_list = list()
    for resource_model in collection_queryset:
        resource_dict = resource_model_to_dict(resource_model)
        collection_list.append(resource_dict)
    return collection_list

def collection_list_to_json(collection_list):
    return simplejson.dumps(collection_list, cls=DjangoJSONEncoder, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT, sort_keys=JSON_SORT_KEYS)

# REST API FUNCTIONS

# TESTBED

def testbed_resource_handler(request):
    if request.method == 'GET':
        resource_dict = OrderedDict()
        resource_dict['uri'] = 'http://' + SERVER_ADDR + ':' + SERVER_PORT + '/'
        resource_dict['media_type'] = MEDIA_TYPE
        resource_dict['name'] = 'TWIST (TKN Wireless Indoor Sensor network Testbed)'
        resource_dict['organization'] = 'Technische Universitaet Berlin'
        
        # collection_queryset = Platform.objects.all()
        # resource_dict['platforms'] = collection_queryset_to_list(collection_queryset)    
        
        resource_dict['platforms'] = 'http://' + SERVER_ADDR + ':' + SERVER_PORT + '/platforms/'
        resource_dict['jobs'] = 'http://' + SERVER_ADDR + ':' + SERVER_PORT + '/jobs/'
        
        resource_json = resource_dict_to_json(resource_dict)
        return HttpResponse(resource_json, content_type=CONTENT_TYPE)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# USER

def user_collection_handler(request):
    if request.method == 'GET':
        collection_queryset = User.objects.all()
        collection_list = collection_queryset_to_list(collection_queryset)
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json, content_type=CONTENT_TYPE)
    else:
        return HttpResponseNotAllowed(['GET'])

# PLATFORM

def platform_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TN API
        native_platform_list = s.getAllPlatforms()
        
        # gets all entries from the TA API
        collection_queryset = Platform.objects.all()
        
        # builds a list of TN API platform_ids
        native_platform_id_list = list()
        for native_platform_dict in native_platform_list:
            native_platform_id_list.append(native_platform_dict['platform_id'])
        
        # deletes all entries that don't exist in the native database (cleaning)
        for resource_model in collection_queryset:
            if resource_model.id not in native_platform_id_list:
                resource_model.delete()
        
        # fetched platforms in the native database and inserts/updates the local database entries (using the same id)
        for native_platform_dict in native_platform_list:
            platform_model = Platform(id = native_platform_dict['platform_id'], name = native_platform_dict['name_long'])
            platform_model.save();

        # gets all the platforms from this database
        collection_queryset = Platform.objects.all()
        collection_list = collection_queryset_to_list(collection_queryset)
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json, content_type=CONTENT_TYPE)
    else:
        return HttpResponseNotAllowed(['GET'])

# PLATFORM

def job_collection_handler(request):
    if request.method == "GET":
        native_collection_list = s.getAllJobs()
        collection_list = list()
        
        for native_job_dict in native_collection_list:
            job_dict = OrderedDict()
            job_dict['uri'] = 'N/A'
            job_dict['media_type'] = MEDIA_TYPE
            job_dict['name'] = native_job_dict['description']
            
            job_dict['owner'] = 'N/A'
            
            # converts datetime to ISO8601 (http://en.wikipedia.org/wiki/ISO_8601)
            job_dict['datetime_from'] = datetime.strptime(native_job_dict['time_begin'].value, "%Y%m%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+01:00")
            job_dict['datetime_to'] = datetime.strptime(native_job_dict['time_end'].value, "%Y%m%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+01:00")
           
            job_dict['platforms'] = list()
            for platform_native_id in native_job_dict['resources']:
                platform_model = Platform.objects.select_related(depth=1).get(native_id=platform_native_id)
                platform_dict = resource_model_to_dict(platform_model)
                job_dict['platforms'].append(platform_dict)
            
            collection_list.append(job_dict)
        
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json, content_type=CONTENT_TYPE)
    else:
        return HttpResponseNotAllowed(['GET'])

# def job_resource_handler(request, id):
#     if request.method == 'GET':
#         resource_model = Job.objects.select_related(depth=1).get(id=int(id))
#         resource_dict = resource_model_to_dict(resource_model)
#         resource_json = resource_dict_to_json(resource_dict)
#         return HttpResponse(resource_json, content_type=CONTENT_TYPE)
#     else:
#         return HttpResponseNotAllowed(['GET'])



