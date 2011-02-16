from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from utils.odict import OrderedDict
from api.models import *
import xmlrpclib
from datetime import datetime

SERVER_NAME = '127.0.0.1:8000'
MEDIA_TYPE = 'application/json'
CONTENT_TYPE = 'application/json;charset=utf-8'
JSON_INDENT = 2

host = '127.0.0.1'
port = '8001'
username = 'conetuser'
password = 'password'
s = xmlrpclib.ServerProxy('http://%s:%s@%s:%s/RPC2' % (username, password, host, port))

# Generic Functions

def model_to_string(resource):
    if isinstance(resource, Testbed):
        return 'testbed'
#    elif isinstance(resource, UserProfile):
#        return 'user'
    elif isinstance(resource, Job):
        return 'job'

def resource_model_to_odict(resource_model, only_head=False):
    resource_odict = OrderedDict()
    resource_odict['uri'] = 'http://' + SERVER_NAME + '/' + model_to_string(resource_model) + 's/' + str(resource_model.id)
    resource_odict['media_type'] = MEDIA_TYPE
    resource_odict['name'] = resource_model.name
    
    if not only_head:
        if resource_model.__class__ == Node:
            resource_odict['platform'] = resource_model_to_odict(resource_model.platform, True)
            resource_odict['image'] = resource_model_to_odict(resource_model.image, True)
            resource_odict['power'] = resource_model.power
        elif resource_model.__class__ == Platform:
            pass
        elif resource_model.__class__ == Image:
            pass
        elif resource_model.__class__ == NodeGroup:
            resource_odict['nodes'] = collection_queryset_to_list(resource_model.nodes.all())
    return resource_odict

def resource_odict_to_model(resource_odict):
    resource_model = Image(name = resource_odict['name'])
    return resource_model
    
def resource_odict_to_json(resource_odict):
    return simplejson.dumps(resource_odict, ensure_ascii=False, indent=JSON_INDENT)

def resource_json_to_odict(resource_json):
    return simplejson.loads(resource_json)

def collection_queryset_to_list(collection_queryset):
    collection_list = list()
    for resource_model in collection_queryset:
        resource_odict = resource_model_to_odict(resource_model, only_head=True)
        collection_list.append(resource_odict)
    return collection_list

def collection_list_to_json(collection_list):
    return simplejson.dumps(collection_list, cls=DjangoJSONEncoder, ensure_ascii=True, indent=JSON_INDENT)


# Testbed

# def testbed_resource_handler(request, id):
#     if request.method == 'GET':
#         resource_model = Testbed.objects.select_related(depth=1).get(id=int(id))
#         resource_odict = resource_model_to_odict(resource_model)
#         resource_json = resource_odict_to_json(resource_odict)
#         return HttpResponse(resource_json, content_type=CONTENT_TYPE)
#     else:
#         return HttpResponseNotAllowed(['GET'])

# Job

def job_collection_handler(request):
    if request.method == "GET":
        collection_list = s.getAllJobs()
        
        for item in collection_list:
            for key in item:
                if isinstance(item[key], xmlrpclib.DateTime):
                    # converts datetime to ISO8601 (http://en.wikipedia.org/wiki/ISO_8601)
                    item[key] = datetime.strptime(item[key].value, "%Y%m%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+01:00")
        
        print simplejson.dumps(collection_list, indent=4)
        exit()
        
        collection_json = collection_list_to_json(collection_list)
        return HttpResponse(collection_json, content_type=CONTENT_TYPE)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

# def job_resource_handler(request, id):
#     if request.method == 'GET':
#         resource_model = Job.objects.select_related(depth=1).get(id=int(id))
#         resource_odict = resource_model_to_odict(resource_model)
#         resource_json = resource_odict_to_json(resource_odict)
#         return HttpResponse(resource_json, content_type=CONTENT_TYPE)
#     else:
#         return HttpResponseNotAllowed(['GET'])



