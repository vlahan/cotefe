import logging
import xmlrpclib
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from testbedserver.api.models import *
from testbedserver.settings import *
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

def testbed_resource_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        testbed = Testbed.objects.all()[0]
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(testbed.to_dict()))
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
    
def platform_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        platform_list = [ p.to_dict(head_only = True) for p in Platform.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(platform_list))
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
            platform = Platform.objects.filter(native_id = native_node_dict['platform_id'])[0]              
            node, created = Node.objects.get_or_create(native_id = native_node_dict['node_id'],
                defaults = {
                    'id' : native_node_dict['serial'],
                    'name' : 'WSN node',
                    'native_id' : native_node_dict['node_id'],
                    'platform' : platform,
                }
            )
        
        # delete nodes that are not present in the native database
        native_node_id_list = [ native_resource_dict['node_id'] for native_resource_dict in native_node_list ]
        Node.objects.exclude(native_id__in = native_node_id_list).delete()
        
        nodes = Node.objects.all()
        
        if 'platform' in request.GET and not (request.GET['platform'] is None):
            nodes = nodes.filter(platform = Platform.objects.get(id = request.GET['platform']))
            
        if 'n' in request.GET and not (request.GET['n'] is None):
            nodes = nodes[:request.GET['n']]
            
        nodes = [ node.to_dict(head_only = True) for node in nodes ]
        
        logging.warning('NUMBER OF NODES RETURNED: %d' % len(nodes))
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(nodes))
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
    
def node_resource_handler(request, node_id):
    
    allowed_methods = ['GET']
    
    try:
        node = Node.objects.get(id = node_id)
    
    except ObjectDoesNotExist:
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
                
        try:
            native_node_dict = proxy.getNode(node.native_id)[0]
        except None:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
    
        node.name = native_node_dict['serial']
        node.platform = Platform.objects.filter(native_id = native_node_dict['platform_id'])[0]
        node.save()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(node.to_dict()))
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

def nodegroup_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        nodegroups = [ nodegroup.to_dict(head_only = True) for nodegroup in NodeGroup.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(nodegroups))
        return response
    
    if request.method == 'POST':
        
        try:
            nodegroup_dict = json.loads(request.raw_post_data)

            nodegroup = NodeGroup(
                id = generate_id(),
                name = nodegroup_dict['name'],
                description = nodegroup_dict['description'],
            )
            nodegroup.save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = nodegroup.get_absolute_url())
            response['Content-Location'] = build_url(path = nodegroup.get_absolute_url())
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
    
def nodegroup_resource_handler(request, nodegroup_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        nodegroup = NodeGroup.objects.get(id = nodegroup_id)
    
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
        response.write(serialize(nodegroup.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        nodegroup_json = request.raw_post_data
        
        try:
            nodegroup_dict = json.loads(nodegroup_json)

            nodegroup.name = nodegroup_dict['name']
            nodegroup.description = nodegroup_dict['description']
            
            nodegroup.save()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(nodegroup.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        nodegroup.delete()
        
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def node_collection_in_nodegroup_handler(request, nodegroup_id):
    
    allowed_methods = ['GET']
    
    try:
        nodegroup = NodeGroup.objects.get(id = nodegroup_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        nodes = [ nodegroup2node.node.to_dict(head_only = True) for nodegroup2node in NodeGroup2Node.nodes.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(nodes))
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
    
def node_resource_in_nodegroup_handler(request, nodegroup_id, node_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        nodegroup = NodeGroup.objects.get(id = nodegroup_id)
        node = Node.objects.get(id = node_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        try:
            NodeGroup2Node.objects.get(nodegroup = nodegroup, node = node)
            
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
        NodeGroup2Node.objects.get_or_create(nodegroup = nodegroup, node = node)
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'DELETE':
        
        try:
            NodeGroup2Node.objects.get(nodegroup = nodegroup, node = node).delete()
            
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
            native_job_list = proxy.getAllJobs()
        except None:
            # 500
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        # updates or creates
        for native_job_dict in native_job_list:
            
            resource_model, created = Job.objects.get_or_create(native_id = native_job_dict['job_id'],
                defaults = {
                    'id' : generate_id(),
                    'native_id' : native_job_dict['job_id'],
                    'name' : '(native job)',
                    'description' : native_job_dict['description'],
                    'datetime_from' : utc_string_to_utc_datetime(native_job_dict['time_begin']),
                    'datetime_to' : utc_string_to_utc_datetime(native_job_dict['time_end']),
                }
            )
            if not created:
                resource_model.description = native_job_dict['description']
                resource_model.time_begin = utc_string_to_utc_datetime(native_job_dict['time_begin'])
                resource_model.time_end = utc_string_to_utc_datetime(native_job_dict['time_end'])
                resource_model.save()
        
        # delete nodes that are not present in the native database
        native_resource_id_list = [ native_resource_dict['job_id'] for native_resource_dict in native_job_list ]
        Job.objects.exclude(native_id__in = native_resource_id_list).delete()

        jobs = [ resource_model.to_dict(head_only = True) for resource_model in Job.objects.all() ]
        
        # generating 200 response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(jobs))
        return response
    
    if request.method == 'POST':
        
        try:
            job_dict = json.loads(request.raw_post_data)
            
            if ('nodes' in job_dict) and not (job_dict['nodes'] is None):
                node_id_list = job_dict['nodes']
                
            platform_native_id_set = set()
            for node_id in node_id_list:
                node = Node.objects.get(id = node_id)
                platform_native_id_set.add(node.platform.native_id)
            
            native_job_dict = dict()
            native_job_dict['description'] = job_dict['description']
            native_job_dict['time_begin'] = job_dict['datetime_from']
            native_job_dict['time_end'] = job_dict['datetime_to']
            native_job_dict['resources'] = list(platform_native_id_set)
            
            try:
                created_job_id_list = proxy.createJob(native_job_dict)
                if len(created_job_id_list) == 0:
                    raise None
            except None:
                # 500
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            job = Job(
                id = generate_id(),
                name = job_dict['name'],
                description = job_dict['description'],
                datetime_from = utc_string_to_utc_datetime(job_dict['datetime_from']),
                datetime_to = utc_string_to_utc_datetime(job_dict['datetime_to']),
                native_id = created_job_id_list[0]['job_id'])
            job.save()
            
            for node_id in node_id_list:
                Job2Node(job = job, node = Node.objects.get(id = node_id)).save()
                
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = job.get_absolute_url())
            response['Content-Location'] = build_url(path = job.get_absolute_url())
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

def job_resource_handler(request, job_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    if job_id == 'current':
        try:
            
            dt_now_utc = get_dt_now_utc()
            
            job = Job.objects.filter(datetime_from__lt = dt_now_utc).filter(datetime_to__gt = dt_now_utc)[0]
            
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(job.to_dict()))
            return response
        
        except None:
            # 404
            response =  HttpResponseNotFound()
            response['Content-Type'] = 'application/json'
            return response
        
    try:
        job = Job.objects.get(id = job_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        
        try:
            native_resource_list = proxy.getJob(job.native_id)
            if len(native_resource_list) == 0:
                # 404
                response = HttpResponseNotFound()
                response['Content-Type'] = 'application/json'
                return response
                
        except None:
            response = HttpResponseServerError()
            response['Content-Type'] = 'application/json'
            return response
        
        native_resource_dict = native_resource_list[0]    
        job.description = native_resource_dict['description']
        job.datetime_from = utc_string_to_utc_datetime(native_resource_dict['time_begin'])
        job.datetime_to = utc_string_to_utc_datetime(native_resource_dict['time_end'])
            
        job.save()
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(job.to_dict()))
        return response
    
    if request.method == 'PUT':

        try:
            job_dict = json.loads(request.raw_post_data)
            
            if ('nodes' in job_dict) and not (job_dict['nodes'] is None):
                node_id_list = job_dict['nodes']
                
            platform_native_id_set = set()
            for node_id in node_id_list:
                node = Node.objects.get(id = node_id)
                platform_native_id_set.add(node.platform.native_id)
                
            native_job_dict = dict()
            native_job_dict['job_id'] = job.native_id
            native_job_dict['description'] = job_dict['description']
            native_job_dict['time_begin'] = job_dict['datetime_from']
            native_job_dict['time_end'] = job_dict['datetime_to']
            native_job_dict['resources'] = list(platform_native_id_set)
                
            try:
                proxy.updateJob(native_job_dict)
            except None:
                response = HttpResponseServerError()
                response['Content-Type'] = 'application/json'
                return response
            
            job.name = job_dict['name']
            job.description = job_dict['description']
            job.datetime_from = utc_string_to_utc_datetime(job_dict['datetime_from'])
            job.datetime_to = utc_string_to_utc_datetime(job_dict['datetime_to'])
            job.save()
            
            for node_id in node_id_list:
                Job2Node(job = job, node = Node.objects.get(id = node_id)).save()

            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(job.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        job.delete()
        
        try:
            proxy.deleteJob(job.native_id)
            
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

def node_collection_in_job_handler(request, job_id):
    
    allowed_methods = ['GET']
    
    try:
        job = Job.objects.get(id = job_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        nodes = [ job2node.node.to_dict(head_only = True) for job2node in Job2Node.objects.filter(job = job) ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(nodes))
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
    
def node_resource_in_job_handler(request, job_id, node_id):
    
    allowed_methods = ['GET']
    
    try:
        job = Job.objects.get(id = job_id)
        node = Node.objects.get(id = node_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        try:
            Job2Node.objects.get(job = job, node = node)
            
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
                id = generate_id(),
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
    
def image_resource_handler(request, image_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(image.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            image_dict = json.loads(request.raw_post_data)

            image.name = image_dict['name']
            image.description = image_dict['description']
            
            image.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(image.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        image.file.delete()
        
        image.delete()
        
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
    
def image_resource_in_node_handler(request, node_id, image_id):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        node  = Node.objects.get(id = node_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'PUT':
            
        node.image = image
        node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ node.native_id ]
        image_path = image.file.file.name
        
        try:
            dt_now_utc = get_dt_now_utc()
            job_native_id = Job.objects.filter(datetime_from__lt = dt_now_utc).filter(datetime_to__gt = dt_now_utc)[0].native_id
        except None:
            # 403
            response =  HttpResponseForbidden()
            response['Content-Type'] = 'application/json'
            return response
        
        try:
            result = proxy.burnImageToNodeList(job_native_id, node_native_id_list, image_path)
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
        
        node.image = None
        node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ node.native_id ]
        image_path = image.file.file.name
        
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
    
def image_resource_in_nodegroup_handler(request, nodegroup_id, image_id):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        nodegroup  = NodeGroup.objects.get(id = nodegroup_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response    
        
    if request.method == 'PUT':
            
        nodegroup.image = image
        nodegroup.save()
        
        for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup):
            nodegroup2node.node.image = image
            nodegroup2node.node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ nodegroup2node.node.native_id for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup) ]
        image_path = image.file.file.name
        
        try:
            dt_now_utc = get_dt_now_utc()
            job_native_id = Job.objects.filter(datetime_from__lt = dt_now_utc).filter(datetime_to__gt = dt_now_utc)[0].native_id
            
        except None:
            # 403
            response =  HttpResponseForbidden()
            response['Content-Type'] = 'application/json'
            return response
        
        try:
            result = proxy.burnImageToNodeList(job_native_id, node_native_id_list, image_path)
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
        
        nodegroup.image = None
        nodegroup.save()
        
        for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup):
            nodegroup2node.node.image = None
            nodegroup2node.node.save()
        
        # call the xmlrpc function with node_id_list and image_path
        
        node_native_id_list = [ nodegroup2node.node.native_id for nodegroup2node in NodeGroup2Node.objects.filter(nodegroup = nodegroup) ]
        image_path = image.file.file.name
        
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

    