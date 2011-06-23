import xmlrpclib
from datetime import datetime
# import base64
# import hashlib
from django.http import HttpResponse, HttpResponseNotAllowed
from testbedserver.api.models import *
from testbedserver.config import *
from testbedserver.utils import *
from testbedserver.proxy import TestbedProxy

proxy = TestbedProxy(
    '%s://%s:%s@%s:%s' % (
        XMLRPC_PROTOCOL,
        XMLRPC_USERNAME,
        XMLRPC_PASSWORD,
        XMLRPC_HOST,
        XMLRPC_PORT
    )
)

# TESTBED

def testbed_resource_handler(request):
    if request.method == 'GET':
        resource_model = TestbedResource.objects.all().get()
        return HttpResponse(serialize(resource_model.to_dict()))
    else:
        return HttpResponseNotAllowed(['GET'])
    
# USER

def user_collection_handler(request):
    if request.method == 'GET':
        collection_queryset = User.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict())
        return HttpResponse(serialize(collection_list))
    else:
        return HttpResponseNotAllowed(['GET'])

def user_resource_handler(request, slug):
    if request.method == 'GET':
        resource_model = User.objects.filter(user__username = slug).get()
        return HttpResponse(serialize(resource_model.to_dict()))
    else:
        return HttpResponseNotAllowed(['GET'])

# PLATFORM

def platform_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_collection_list = proxy.getAllPlatforms()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
        
        # gets all entries from the TA API
        collection_queryset = PlatformResource.objects.all()
        
        # builds a list of TN API platform ids
        native_resource_id_list = list()
        for native_resource_dict in native_collection_list:
            native_resource_id_list.append(native_resource_dict['platform_id'])
        
        # deletes all entries that don't exist in the native database (cleaning)
        for resource_model in collection_queryset:
            if resource_model.id not in native_resource_id_list:
                resource_model.delete()
        
        # fetches platforms in the native database and inserts/updates the local database entries (using the same id)
        for native_resource_dict in native_collection_list:
            resource_model = PlatformResource(
                id = native_resource_dict['platform_id'],
                name = native_resource_dict['name_long'],
                tinyos_name = native_resource_dict['name_tinyos'])
            resource_model.save();

        # gets all the platforms from this database
        collection_queryset = PlatformResource.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict())
        return HttpResponse(serialize(collection_list))
    else:
        return HttpResponseNotAllowed(['GET'])
    
def platform_resource_handler(request, slug):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_resource_dict = proxy.getPlatformById(slug)
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
            
        # gets the entry from the the TA API
        resource_model = PlatformResource.objects.get(pk = slug)
        
        # deletes the entry if it does not exist in the native database (cleaning)
        if resource_model.id != native_resource_dict['platform_id']:
            resource_model.delete()
        
        # fetches platforms in the native database and inserts/updates the local database entries (using the same id)
        resource_model = PlatformResource(
            id = native_resource_dict['platform_id'],
            name = native_resource_dict['name_long'],
            tinyos_name = native_resource_dict['name_tinyos'])
        resource_model.save();
            
        resource_model = PlatformResource.objects.get(pk = slug)
        return HttpResponse(serialize(resource_model.to_dict()))
    else:
        return HttpResponseNotAllowed(['GET'])
# JOB

def job_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_collection_list = proxy.getAllJobs()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString) 
            
        # gets all entries from the TA API
        collection_queryset = JobResource.objects.all()
        
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
            resource_model = JobResource(
                id = native_resource_dict['job_id'],
                name = native_resource_dict['description'],
                datetime_from = native_resource_dict['time_begin'],
                datetime_to   = native_resource_dict['time_end'],
            )
            resource_model.save();

        # gets all the platforms from this database
        collection_queryset = JobResource.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict())
        return HttpResponse(serialize(collection_list))
        
    elif request.method == 'POST':
        pass
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    
def job_resource_handler(request, slug):
    if request.method == 'GET':
        # gets all entries from the TN API
        try:
            native_resource_dict = proxy.getJobById(slug)
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
            
        # gets the entry from the the TA API
        resource_model = JobResource.objects.get(pk = slug)
        
        # deletes the entry if it doeas not exist in the native database (cleaning)
        if resource_model.id != native_resource_dict['platform_id']:
            resource_model.delete()
        
        # fetches platforms in the native database and inserts/updates the local database entries (using the same id)
        resource_model = JobResource(
            id = native_resource_dict['job_id'],
            name = native_resource_dict['description'],
            datetime_from = native_resource_dict['time_begin'],
            datetime_to   = native_resource_dict['time_end']
        )
        resource_model.save()
            
        resource_model = JobResource.objects.get(pk = slug)
        return HttpResponse(serialize(resource_model.to_dict()))
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])