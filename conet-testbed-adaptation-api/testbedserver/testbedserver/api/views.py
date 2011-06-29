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
    
    allowed_methods = ['GET']
    
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':
        resource_model = Testbed.objects.all()[0]
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
# PLATFORM
def platform_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        try:
            native_collection_list = proxy.getAllPlatforms()
        except xmlrpclib.Fault, err:
            print "XMLRPC Error (%s):%s" % (err.faultCode, err.faultString)
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        for native_resource_dict in native_collection_list:
            resource_model, created = Platform.objects.get_or_create(native_id = native_resource_dict['platform_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'native_id' : native_resource_dict['platform_id'],
                    'name' : native_resource_dict['name_long'],
                    'tinyos_name' : native_resource_dict['name_tinyos'],
                }
            )
            if not created:
                resource_model.name = native_resource_dict['name_long']
                resource_model.tinyos_name = native_resource_dict['name_tinyos']
                resource_model.save()
        
        native_resource_id_list = [ native_resource_dict['platform_id'] for native_resource_dict in native_collection_list ]
        Platform.objects.exclude(native_id__in = native_resource_id_list).delete()

        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in Platform.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    else:
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def platform_resource_handler(request, platform_uid):
    
    allowed_methods = ['GET']
    
    try:
        resource_model = Platform.objects.get(uid = platform_uid)
    
    except ObjectDoesNotExist:
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
                
        try:
            native_resource_dict = proxy.getPlatformById(resource_model.native_id)[0]
        except Exception:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        resource_model.name = native_resource_dict['name_long']
        resource_model.tinyos_name = native_resource_dict['name_tinyos']
        resource_model.save()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
# NODE
def node_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        # gets all resources from the native database
        try:
            native_collection_list = proxy.getAllNodes()
        except Exception:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_resource_dict in native_collection_list:
            
            try:
                platform_model = Platform.objects.get(native_id = native_resource_dict['platform_id'])
            except ObjectDoesNotExist:
                try:
                    native_resource_dict = proxy.getPlatformById(native_resource_dict['platform_id'])[0]
                except Exception:
                    response = HttpResponseServerError()
                    response['Content-Type'] = 'application/json'
                    return response
                
                platform_model, created = Platform.objects.get_or_create(native_id = native_resource_dict['platform_id'],
                    defaults = {
                        'uid' : generate_uid(),
                        'native_id' : native_resource_dict['platform_id'],
                        'name' : native_resource_dict['name_long'],
                        'tinyos_name' : native_resource_dict['name_tinyos']})
                if not created:
                    platform_model.name = native_resource_dict['name_long']
                    platform_model.tinyos_name = native_resource_dict['name_tinyos']
                    platform_model.save()
            
            resource_model, created = Node.objects.get_or_create(native_id = native_resource_dict['node_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'native_id' : native_resource_dict['node_id'],
                    'serial' : native_resource_dict['serial'],
                    'platform' : platform_model
                }
            )
            if not created:
                resource_model.serial = native_resource_dict['serial']
                resource_model.platform = platform_model
                resource_model.save()
        
        # delete nodes that are not present in the native database
        native_resource_id_list = [ native_resource_dict['node_id'] for native_resource_dict in native_collection_list ]
        Node.objects.exclude(native_id__in = native_resource_id_list).delete()

        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in Node.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def node_resource_handler(request, node_uid):
    
    allowed_methods = ['GET']
    
    try:
        resource_model = Node.objects.get(uid = node_uid)
    
    except ObjectDoesNotExist:
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
                
        try:
            native_resource_dict = proxy.getNodeById(resource_model.native_id)[0]
        except Exception:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        try:
            platform_model = Platform.objects.get(native_id = native_resource_dict['platform_id'])
        except ObjectDoesNotExist:
            try:
                native_platform_dict = proxy.getPlatformById(native_resource_dict['platform_id'])[0]
            except Exception:
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            platform_model, created = Platform.objects.get_or_create(native_id = native_resource_dict['platform_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'native_id' : native_platform_dict['platform_id'],
                    'name' : native_platform_dict['name_long'],
                    'tinyos_name' : native_platform_dict['name_tinyos']})
            if not created:
                platform_model.name = native_platform_dict['name_long']
                platform_model.tinyos_name = native_platform_dict['name_tinyos']
                platform_model.save()
    
        resource_model.serial = native_resource_dict['serial']
        resource_model.platform = platform_model
        resource_model.save()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    
    if request.method == 'OPTIONS':
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
# NODEGROUP
def nodegroup_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in NodeGroup.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'POST':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model = NodeGroup(
                uid = generate_uid(),
                name = resource_dict['name'],
                description = resource_dict['description'])
            resource_model.save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Type'] = 'application/json'
            return response
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def nodegroup_resource_handler(request, nodegroup_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource_model = NodeGroup.objects.get(uid = nodegroup_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model.name = resource_dict['name']
            resource_model.description = resource_dict['description']
            
            resource_model.save()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
            
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        resource_model.delete()
        
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def node_collection_in_nodegroup_handler(request, nodegroup_uid):
    
    allowed_methods = ['GET']
    
    try:
        nodegroup_model = NodeGroup.objects.get(uid = nodegroup_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        node_collection_list = [ nodegroup2node.node.to_dict(head_only = True) for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup_model) ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(node_collection_list))
        return response
        
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response        
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def node_resource_in_nodegroup_handler(request, nodegroup_uid, node_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        nodegroup_model = NodeGroup.objects.get(uid = nodegroup_uid)
        node_model = Node.objects.get(uid = node_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        try:
            NodeGroup2Node.objects.get(nodegroup = nodegroup_model, node = node_model)
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            return response
        except ObjectDoesNotExist:
            # 404
            response = HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
        
    
    if request.method == 'PUT':
        
        try:
            resource_model, created = NodeGroup2Node.objects.get_or_create(nodegroup = nodegroup_model, node = node_model)
                
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            return response
        except ObjectDoesNotExist:
            # 404
            response = HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        try:
            NodeGroup2Node.objects.get(nodegroup = nodegroup_model, node = node_model).delete()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            return response
        except ObjectDoesNotExist:
            # 404
            response = HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

# JOB
def job_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        try:
            native_collection_list = proxy.getAllJobs()
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_resource_dict in native_collection_list:
            
            resource_model, created = Job.objects.get_or_create(native_id = native_resource_dict['job_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'native_id' : native_resource_dict['job_id'],
                    'name' : 'native job',
                    'description' : native_resource_dict['description'],
                    'datetime_from' : native_resource_dict['time_begin'],
                    'datetime_to' : native_resource_dict['time_end'],
                }
            )
            if not created:
                resource_model.name = 'native job'
                resource_model.description = native_resource_dict['description']
                resource_model.time_begin = native_resource_dict['time_begin']
                resource_model.time_end = native_resource_dict['time_end']
                resource_model.save()
        
        # delete nodes that are not present in the native database
        native_resource_id_list = [ native_resource_dict['job_id'] for native_resource_dict in native_collection_list ]
        Job.objects.exclude(native_id__in = native_resource_id_list).delete()

        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in Job.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
        if request.method == 'POST':
            try:
                resource_model = Job(
                    uid = generate_uid(),
                    name = request.POST['name'],
                    description = request.POST['description'])
                
                # file is optional, can be updated later
                try:
                    resource_model.file = request.FILES['file']
                except Exception:
                    pass
                resource_model.save()
                
                # 201
                response = HttpResponse(status=201)
                response['Location'] = build_url(path = resource_model.get_absolute_url())
                response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
                response['Content-Type'] = 'application/json'
                return response
            except Exception:
                # 400
                response = HttpResponseBadRequest()
                response['Content-Type'] = 'application/json'
                return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

def job_resource_handler(request, job_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource_model = Job.objects.get(uid = job_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        
        try:
            native_resource_dict = proxy.getJobById(resource_model.native_id)[0]
        except None:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        resource_model.name = 'native job'
        resource_model.description = native_resource_dict['description']
        resource_model.datetime_from = native_resource_dict['time_begin']
        resource_model.datetime_to = native_resource_dict['time_end']
            
        resource_model.save()
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)
            
            native_resource_dict = dict()
            native_resource_dict['job_id'] = resource_model.native_id
            native_resource_dict['description'] = resource_model.description
            native_resource_dict['time_begin'] = resource_model.datetime_from
            native_resource_dict['time_end'] = resource_model.datetime_to
            
            try:
                proxy.updateJobById(native_resource_dict)
            except None:
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response

            resource_model.name = resource_dict['name']
            resource_model.description = resource_dict['description']
            resource_model.datetime_from = resource_dict['datetime_from']
            resource_model.datetime_to = resource_dict['datetime_to']
            
            resource_model.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
            
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        resource_model.delete()
        
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
# IMAGE
def image_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        collection_list = [ resource_model.to_dict(head_only = True) for resource_model in Image.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'POST':
                
        try:
            resource_model = Image(
                uid = generate_uid(),
                name = request.POST['name'],
                description = request.POST['description'])
            
            # file is optional, can be updated later
            try:
                resource_model.file = request.FILES['file']
            except Exception:
                pass
            resource_model.save()
            
            # 201
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Type'] = 'application/json'
            return response
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def image_resource_handler(request, image_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource_model = Image.objects.get(uid = image_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model.name = resource_dict['name']
            resource_model.description = resource_dict['description']
            
            resource_model.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
            
        except Exception:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        resource_model.file.delete()
        
        resource_model.delete()
        
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'OPTIONS':
        # 204
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response