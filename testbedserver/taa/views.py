import xmlrpclib
from datetime import datetime
# import base64
# import hashlib
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from testbedserver.taa.models import Platform, Job
from django.contrib.auth.models import User
from testbedserver.utils.odict import OrderedDict

# INFORMATION FOR BUILDING URLS
PROTOCOL = 'http'
# SERVER_ADDR = 'www.twist.tu-berlin.de'
SERVER_ADDR = 'localhost'
SERVER_PORT = '8001'
SERVER_PATH = PROTOCOL + '://' + SERVER_ADDR + ':' + SERVER_PORT
MEDIA_TYPE = 'application/json'

# JSON FORMAT CONFIGURATION
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

# UTILITY FUNCTIONS

def resource_model_to_dict(resource_model, head_only=False):
    resource_dict = OrderedDict()
    
    resource_dict['uri'] = SERVER_PATH + resource_model.get_absolute_url()
    resource_dict['media_type'] = MEDIA_TYPE
    
    if isinstance(resource_model, User):
        resource_dict['name'] = resource_model.username
        
    elif isinstance(resource_model, Platform):
        resource_dict['name'] = resource_model.name
        
    elif isinstance(resource_model, Job):
        resource_dict['name'] = resource_model.name
        
        
    if not head_only:
        if isinstance(resource_model, User):
            resource_dict['first_name'] = resource_model.first_name
            resource_dict['last_name'] = resource_model.last_name
            resource_dict['email'] = resource_model.email
            
        elif isinstance(resource_model, Platform):
            resource_dict['tinyos_name'] = resource_model.tinyos_name
        
        elif isinstance(resource_model, Job):
            # resource_dict['owner'] = resource_model.owner
            resource_dict['datetime_from'] = resource_model.datetime_from
            resource_dict['datetime_to'] = resource_model.datetime_to
            
            resource_dict['platforms'] = collection_queryset_to_list(resource_model.platforms.all())

    return resource_dict
    
def resource_dict_to_json(resource_dict):
    return simplejson.dumps(resource_dict, ensure_ascii=JSON_ENSURE_ASCII,
                            indent=JSON_INDENT, sort_keys=JSON_SORT_KEYS)

def resource_json_to_dict(resource_json):
    return simplejson.loads(resource_json)

def collection_queryset_to_list(collection_queryset):
    collection_list = list()
    for resource_model in collection_queryset:
        resource_dict = resource_model_to_dict(resource_model, head_only=True)
        collection_list.append(resource_dict)
    return collection_list

def collection_list_to_json(collection_list):
    return simplejson.dumps(collection_list, cls=DjangoJSONEncoder,
                            ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT, sort_keys=JSON_SORT_KEYS)

# REST API FUNCTIONS

# TESTBED

def testbed_resource_handler(request):
    if request.method == 'GET':
        resource_dict = OrderedDict()
        resource_dict['uri'] = SERVER_PATH + '/'
        resource_dict['media_type'] = MEDIA_TYPE
        resource_dict['name'] = 'TWIST (TKN Wireless Indoor Sensor network Testbed)'
        resource_dict['organization'] = 'Technische Universitaet Berlin'
        
        # collection_queryset = Platform.objects.all()
        # resource_dict['platforms'] = collection_queryset_to_list(collection_queryset)    
        
        resource_dict['platforms'] = SERVER_PATH + '/platforms/'
        resource_dict['jobs'] = SERVER_PATH + '/jobs/'
        
        resource_json = resource_dict_to_json(resource_dict)
        return HttpResponse(resource_json)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# USER

def user_collection_handler(request):
    if request.method == 'GET':
        collection_queryset = User.objects.all()
        collection_list = collection_queryset_to_list(collection_queryset)
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json)
    else:
        return HttpResponseNotAllowed(['GET'])

# PLATFORM

def platform_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_collection_list = tn_server.getAllPlatforms()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString) 
        
        # gets all entries from the TA API
        collection_queryset = Platform.objects.all()
        
        # builds a list of TN API platform ids
        native_resource_id_list = list()
        for native_resource_dict in native_collection_list:
            native_resource_id_list.append(native_resource_dict['platform_id'])
        
        # deletes all entries that don't exist in the native database (cleaning)
        for resource_model in collection_queryset:
            if resource_model.id not in native_resource_id_list:
                resource_model.delete()
        
        # fetched platforms in the native database and inserts/updates the local database entries (using the same id)
        for native_resource_dict in native_collection_list:
            resource_model = Platform(id = native_resource_dict['platform_id'], name = native_resource_dict['name_long'], tinyos_name = native_resource_dict['name_tinyos'])
            resource_model.save();

        # gets all the platforms from this database
        collection_queryset = Platform.objects.all()
        collection_list = collection_queryset_to_list(collection_queryset)
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json)
    else:
        return HttpResponseNotAllowed(['GET'])
    
def platform_resource_handler(request, slug):
    if request.method == 'GET':
        # gets all entries from the TN API
        resource_model = Platform.objects.get(pk=slug)
        resource_dict = resource_model_to_dict(resource_model)
        resource_json = resource_dict_to_json(resource_dict)
        return HttpResponse(resource_json)
    else:
        return HttpResponseNotAllowed(['GET'])

# JOB

def job_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_collection_list = tn_server.getAllJobs()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString) 
            
        # gets all entries from the TA API
        collection_queryset = Job.objects.all()
        
        # builds a list of TN API job ids
        native_resource_id_list = list()
        for native_resource_dict in native_collection_list:
            native_resource_id_list.append(native_resource_dict['job_id'])
        
        # deletes all entries that don't exist in the native database (cleaning)
        for resource_model in collection_queryset:
            if resource_model.id not in native_resource_id_list:
                resource_model.delete()
        
        # fetched jobs in the native database and inserts/updates the local database entries (using the same id)
        for native_resource_dict in native_collection_list:
            
            platform_list = list()
            for native_platform_id in native_resource_dict['resources']:
                platform_list.append(Platform.objects.get(pk=native_platform_id))
                
            resource_model = Job(
                id = native_resource_dict['job_id'],
                name = native_resource_dict['description'],
                datetime_from = native_resource_dict['time_begin'],
                datetime_to   = native_resource_dict['time_end'],
                # platforms = platform_list
            )
            resource_model.save();
            resource_model.platforms = platform_list
            resource_model.save();

        # gets all the platforms from this database
        collection_queryset = Job.objects.all()
        collection_list = collection_queryset_to_list(collection_queryset)
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    
def job_resource_handler(request, slug):
    if request.method == 'GET':
        # gets all entries from the TN API
        resource_model = Job.objects.select_related(depth=1).get(pk=slug)
        resource_dict = resource_model_to_dict(resource_model)
        resource_json = resource_dict_to_json(resource_dict)
        return HttpResponse(resource_json)
    else:
        return HttpResponseNotAllowed(['GET'])
