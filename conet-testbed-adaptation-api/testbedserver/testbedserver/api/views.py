import logging
import xmlrpclib
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from testbedserver.api.models import *
from testbedserver.config import *
from testbedserver.utils import *
from testbedserver.proxy import TestbedProxy
from django.contrib.auth.models import UserManager

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
        resource_model = Testbed.objects.all()[0]
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    else:
        return HttpResponseNotAllowed(['GET'])
    
# PLATFORM
def platform_collection_handler(request):
    if request.method == 'GET':
        # gets all entries from the TNA in a list of dictionaries
        try:
            native_collection_list = proxy.getAllPlatforms()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # gets all entries from the TAA in a list of dictionaries
        collection_queryset = Platform.objects.all() 
        
        # for each TNA resource..
        for native_resource_dict in native_collection_list:
            # if it is already in the TA database it gets updated
            try:
                resource_model = Platform.objects.get(native_id = native_resource_dict['platform_id'])
                resource_model.name = native_resource_dict['name_long']
                resource_model.tinyos_name = native_resource_dict['name_tinyos']
            # otherwise it gets created
            except ObjectDoesNotExist:
                resource_model = Platform()
                resource_model.uid = generate_uid()
                resource_model.native_id = native_resource_dict['platform_id']
                resource_model.name = native_resource_dict['name_long']
                resource_model.tinyos_name = native_resource_dict['name_tinyos']
            # in both cases I need to save
            # this loops makes sure that I generate a new uuid
            while 1:
                try:
                    resource_model.save()
                    break
                except Exception:
                    logging.debug("uid was duplicate!")
                    resource_model.uid = generate_uid()
                    resource_model.save()
            
        # builds a list of TN API platform ids
        native_resource_id_list = list()
        for native_resource_dict in native_collection_list:
            native_resource_id_list.append(native_resource_dict['platform_id'])
                
        # deletes all entries that don't exist in the native database (cleaning)
        for resource_model in collection_queryset:
            if resource_model.native_id not in native_resource_id_list:
                resource_model.delete()

        # gets all the platforms from this database
        collection_queryset = Platform.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict(head_only = True))
            
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    else:
        return HttpResponseNotAllowed(['GET'])
    
def platform_resource_handler(request, platform_id):
    if request.method == 'GET':
        try:
            resource_model = Platform.objects.get(uid = platform_id)
            
            # has to check whether the resource is still in the native database. 
            try:
                native_resource_dict = proxy.getPlatformById(resource_model.native_id)[0]
            except xmlrpclib.Fault, err:
                print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            # if yes, needs to update
            resource_model.name = native_resource_dict['name_long']
            resource_model.tinyos_name = native_resource_dict['name_tinyos']
            resource_model.save()
            
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
        except ObjectDoesNotExist:
            # response = HttpResponseNotFound()
            response = HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
    else:
        return HttpResponseNotAllowed(['GET'])
    
# NODE
def node_collection_handler(request):
    if request.method == 'GET':
        
        # gets all resources from the native database
        try:
            native_collection_list = proxy.getAllNodes()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
            
            # generating 500 response
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_resource_dict in native_collection_list:
            resource_model, created = Node.objects.get_or_create(native_id = native_resource_dict['node_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'native_id' : native_resource_dict['node_id'],
                    'serial' : native_resource_dict['serial']
                }
            )
            if not created:
                resource_model.serial = native_resource_dict['serial']
                resource_model.save()
        
        # delete nodes that are not present in the native database
        native_resource_id_list = [ native_resource_dict['node_id'] for native_resource_dict in native_collection_list ]
        Node.objects.exclude(native_id__in = native_resource_id_list).delete()

        # gets all resources
        collection_queryset = Node.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict(head_only = True))
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    else:
        return HttpResponseNotAllowed(['GET'])
    
def node_resource_handler(request, node_id):
    if request.method == 'GET':
        try:
            resource_model = Node.objects.get(uid = node_id)
            
            # has to check whether the resource is still in the native database. 
            try:
                native_resource_dict = proxy.getNodeById(resource_model.native_id)[0]
            except xmlrpclib.Fault, err:
                print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            # if yes, needs to update
            resource_model.serial = native_resource_dict['serial']
            
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
        except ObjectDoesNotExist:
            # response = HttpResponseNotFound()
            response = HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
    else:
        return HttpResponseNotAllowed(['GET'])
    
def node_collection_in_nodegroup_handler(request, nodegroup_id):
    if request.method == 'GET':
        return HttpResponse('nodegroup_id = ' + nodegroup_id + ', all nodes')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def node_resource_in_nodegroup_handler(request, nodegroup_id, node_id):
    if request.method == 'GET':
        return HttpResponse('nodegroup_id = ' + nodegroup_id + ', node_id = ' + node_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# NODEGROUP

def nodegroup_collection_handler(request):
    if request.method == 'GET':
        return HttpResponse('all nodegroups')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def nodegroup_resource_handler(request, nodegroup_id):
    if request.method == 'GET':
        return HttpResponse('nodegroup_id = '+ nodegroup_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# JOB

def job_collection_handler(request):
    if request.method == 'GET':
        return HttpResponse('all jobs')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def job_resource_handler(request, job_id):
    if request.method == 'GET':
        return HttpResponse('job_id = '+ job_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# IMAGE
    
def image_collection_handler(request):
    if request.method == 'GET':
        return HttpResponse('all images')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def image_resource_handler(request, image_id):
    if request.method == 'GET':
        return HttpResponse('image_id = '+ image_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# TRACE
    
def trace_collection_in_job_handler(request, job_id):
    if request.method == 'GET':
        return HttpResponse('job_id = ' + job_id + ', all traces')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def trace_resource_in_job_handler(request, job_id, trace_id):
    if request.method == 'GET':
        return HttpResponse('job_id = ' + job_id + ', trace_id = ' + trace_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    
# LOG
    
def log_collection_in_job_handler(request, job_id):
    if request.method == 'GET':
        return HttpResponse('job_id = ' + job_id + ', all logs')
    else:
        return HttpResponseNotAllowed(['GET'])
    
def log_resource_in_job_handler(request, job_id, log_id):
    if request.method == 'GET':
        return HttpResponse('job_id = ' + job_id + ', log_id = ' + log_id)
    else:
        return HttpResponseNotAllowed(['GET'])
    


# USER
#def user_collection_handler(request):
#    if request.method == 'GET':
#        collection_queryset = User.objects.all()
#        collection_list = list()
#        for resource_model in collection_queryset:
#            collection_list.append(resource_model.to_dict())
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(serialize(collection_list))
#        return response
#    else:
#        return HttpResponseNotAllowed(['GET'])
#
#def user_resource_handler(request, id):
#    if request.method == 'GET':
#        resource_model = User.objects.filter(user__username = id).get()
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(serialize(resource_model.to_dict()))
#        return response
#    else:
#        return HttpResponseNotAllowed(['GET'])

# IMAGE
#def image_collection_handler(request):
#    if request.method == 'GET':
#        collection_queryset = Image.objects.all()
#        collection_list = list()
#        for resource_model in collection_queryset:
#            collection_list.append(resource_model.to_dict())
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write(serialize(collection_list))
#    elif request.method == 'POST':
#        image_model = Image()
#        image_model.name = request.POST['name']
#        image_model.file = request.FILES['file']
#        image_model.save()
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        response.write('ok')
#    else:
#        response = HttpResponseNotAllowed(['GET', 'POST'])
#    return response
        

    
# JOB

#def job_collection_handler(request):
#    if request.method == 'GET':
#        # gets all entries from the TN API
#        try:
#            native_collection_list = proxy.getAllJobs()
#        except xmlrpclib.Fault, err:
#            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString) 
#            
#        # gets all entries from the TA API
#        collection_queryset = Job.objects.all()
#        
#        # builds a list of TN API job ids
#        native_resource_id_list = list()
#        for native_resource_dict in native_collection_list:
#            native_resource_id_list.append(native_resource_dict['job_id'])
#        
#        # deletes all entries that don't exist in the native database (cleaning)
#        for resource_model in collection_queryset:
#            if resource_model.id not in native_resource_id_list:
#                resource_model.delete()
#        
#        # fetched jobs in the native database and inserts/updates the local database entries (using the same id)
#        for native_resource_dict in native_collection_list:
#            resource_model = Job(
#                id = native_resource_dict['job_id'],
#                name = native_resource_dict['description'],
#                datetime_from = native_resource_dict['time_begin'],
#                datetime_to   = native_resource_dict['time_end'],
#            )
#            resource_model.save();
#
#        # gets all the platforms from this database
#        collection_queryset = Job.objects.all()
#        collection_list = list()
#        for resource_model in collection_queryset:
#            collection_list.append(resource_model.to_dict())
#        return HttpResponse(serialize(collection_list))
#        
#    elif request.method == 'POST':
#        pass
#    else:
#        return HttpResponseNotAllowed(['GET', 'POST'])
#    
#def job_resource_handler(request, slug):
#    if request.method == 'GET':
#        # gets all entries from the TN API
#        try:
#            native_resource_dict = proxy.getJobById(slug)
#        except xmlrpclib.Fault, err:
#            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
#            
#        # gets the entry from the the TA API
#        resource_model = Job.objects.get(pk = slug)
#        
#        # deletes the entry if it doeas not exist in the native database (cleaning)
#        if resource_model.id != native_resource_dict['platform_id']:
#            resource_model.delete()
#        
#        # fetches platforms in the native database and inserts/updates the local database entries (using the same id)
#        resource_model = Job(
#            id = native_resource_dict['job_id'],
#            name = native_resource_dict['description'],
#            datetime_from = native_resource_dict['time_begin'],
#            datetime_to   = native_resource_dict['time_end']
#        )
#        resource_model.save()
#            
#        resource_model = Job.objects.get(pk = slug)
#        return HttpResponse(serialize(resource_model.to_dict()))
#    elif request.method == 'PUT':
#        pass
#    elif request.method == 'DELETE':
#        pass
#    else:
#        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])