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
    
    if request.method == 'GET':
        resource_model = Testbed.objects.all()[0]
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
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
            native_resource_dict = proxy.getPlatform(resource_model.native_id)[0]
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
        
        try:
            native_node_list = proxy.getAllNodes()
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_node_dict in native_node_list:
            
            try:
                platform_model = Platform.objects.get(native_id = native_node_dict['platform_id'])
            except ObjectDoesNotExist:
                try:
                    native_platform_dict = proxy.getPlatform(native_node_dict['platform_id'])[0]
                except Exception:
                    response = HttpResponseServerError()
                    response['Content-Type'] = 'application/json'
                    return response
                
                platform_model, created = Platform.objects.get_or_create(native_id = native_platform_dict['platform_id'],
                    defaults = {
                        'uid' : generate_uid(),
                        'native_id' : native_platform_dict['platform_id'],
                        'name' : native_platform_dict['name_long'],
                        'tinyos_name' : native_platform_dict['name_tinyos']})
                if not created:
                    platform_model.name = native_platform_dict['name_long']
                    platform_model.tinyos_name = native_platform_dict['name_tinyos']
                    platform_model.save()
            
            resource_model, created = Node.objects.get_or_create(native_id = native_node_dict['node_id'],
                defaults = {
                    'uid' : generate_uid(),
                    'name' : native_node_dict['serial'],
                    'native_id' : native_node_dict['node_id'],
                    'platform' : platform_model,
                }
            )
            if not created:
                resource_model.name = native_node_dict['serial']
                resource_model.platform = platform_model
                resource_model.save()
        
        # delete nodes that are not present in the native database
        native_node_id_list = [ native_resource_dict['node_id'] for native_resource_dict in native_node_list ]
        Node.objects.exclude(native_id__in = native_node_id_list).delete()
        
        if 'platform' in request.GET and not (request.GET is None):
            node_list = [ node_model.to_dict(head_only = True) for node_model in Node.objects.filter(platform = Platform.objects.get(uid = request.GET['platform'])) ]
        else:
            node_list = [ node_model.to_dict(head_only = True) for node_model in Node.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(node_list))
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
            native_resource_dict = proxy.getNode(resource_model.native_id)[0]
        except Exception:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        try:
            platform_model = Platform.objects.get(native_id = native_resource_dict['platform_id'])
        except ObjectDoesNotExist:
            try:
                native_platform_dict = proxy.getPlatform(native_resource_dict['platform_id'])[0]
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
    
        resource_model.name = native_resource_dict['serial']
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
                description = resource_dict['description'],
            )
            resource_model.save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Type'] = 'application/json'
            return response
        except None:
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
        except Exception:
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
                    'name' : '(native job)',
                    'description' : native_resource_dict['description'],
                    'datetime_from' : native_resource_dict['time_begin'],
                    'datetime_to' : native_resource_dict['time_end'],
                }
            )
            if not created:
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
    
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model = Job(
                uid = generate_uid(),
                name = resource_dict['name'],
                description = resource_dict['description'],
                datetime_from = resource_dict['datetime_from'],
                datetime_to = resource_dict['datetime_to'])
            resource_model.save()
            
            native_resource_dict = dict()
            native_resource_dict['description'] = resource_model.description
            native_resource_dict['time_begin'] = resource_model.datetime_from
            native_resource_dict['time_end'] = resource_model.datetime_to
            native_resource_dict['resources'] = [1,2,3,4,5]
            
            try:
                created_job_id_list = proxy.createJob(native_resource_dict)
                if len(created_job_id_list) == 0:
                    pass
                else:
                    job_native_id = created_job_id_list[0]['job_id']
            except None:
                # 500
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            resource_model.native_id = job_native_id
            resource_model.save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Type'] = 'application/json'
            return response
        except None:
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
            native_resource_list = proxy.getJob(resource_model.native_id)
            if len(native_resource_list) == 0:
                # 404
                response = HttpResponseNotFound()
                response['Content-Type'] = 'application/json'
                return response
                
        except Exception:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        native_resource_dict = native_resource_list[0]    
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
            # first thing, I update the ta database
            
            resource_dict = json.loads(resource_json)
            
            resource_model.name = resource_dict['name']
            resource_model.description = resource_dict['description']
            resource_model.datetime_from = resource_dict['datetime_from']
            resource_model.datetime_to = resource_dict['datetime_to']
            
            resource_model.save()
            
            # then I upadate the job on the native database
            
            native_resource_dict = dict()
            native_resource_dict['job_id'] = resource_model.native_id
            native_resource_dict['description'] = resource_model.description
            native_resource_dict['time_begin'] = resource_model.datetime_from
            native_resource_dict['time_end'] = resource_model.datetime_to
            native_resource_dict['resources'] = [1,2,3,4,5]
            
            try:
                proxy.updateJob(native_resource_dict)
            except None:
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response

            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        resource_model.delete()
        
        try:
            proxy.deleteJob(resource_model.native_id)
            
        except None:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
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
                description = request.POST['description'],
                file = request.FILES['file'])
            
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
    
def image_resource_in_node_handler(request, node_uid, image_uid):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        node_model  = Node.objects.get(uid = node_uid)
        image_model = Image.objects.get(uid = image_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'PUT':
            
        node_model.image = image_model
        node_model.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ node_model.native_id ]
        image_path = image_model.file.file.name
        
        try:
            result = proxy.burnImageToNodeList(image_path, node_native_id_list)
            logging.warning(result)
            
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
         
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'DELETE':
        
        node_model.image = None
        node_model.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ node_model.native_id ]
        image_path = image_model.file.file.name
        
        try:
            proxy.burnImageToNodeList(None, node_native_id_list)
            
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
            
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
    
def image_resource_in_nodegroup_handler(request, nodegroup_uid, image_uid):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        nodegroup_model  = NodeGroup.objects.get(uid = nodegroup_uid)
        image_model = Image.objects.get(uid = image_uid)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response    
        
    if request.method == 'PUT':
            
        nodegroup_model.image = image_model
        nodegroup_model.save()
        
        for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup_model):
            nodegroup2node.node.image = image_model
            nodegroup2node.node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ nodegroup2node.node.native_id for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup_model) ]
        image_path = image_model.file.file.name
        
        try:
            result = proxy.burnImageToNodeList(image_path, node_native_id_list)
            logging.warning(result)
            
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
         
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'DELETE':
        
        nodegroup_model.image = None
        nodegroup_model.save()
        
        for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup_model):
            nodegroup2node.node.image = None
            nodegroup2node.node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ nodegroup2node.node.native_id for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup_model) ]
        image_path = image_model.file.file.name
        
#        try:
#            proxy.burnImageToNodeList(None, node_native_id_list)
#            
#        except None:
#            # 500
#            response = HttpResponseServerError()
#            response['Content-Type'] = 'application/json'
#            return response
            
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