import httplib2
import logging
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from api.models import *
from settings import *
from utils import *


def federation_resource_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        resource_model = Federation.objects.all()[0]
        
        # 200
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    

def testbed_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        testbed_list = [ testbed_model.to_dict(head_only = True) for testbed_model in Testbed.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(testbed_list))
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
    
def testbed_resource_handler(request, testbed_id):
    
    allowed_methods = ['GET']
    
    try:
        testbed_model = Testbed.objects.get(id = testbed_id)
    
    except ObjectDoesNotExist:
        
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        testbed_proxy = httplib2.Http()
        # testbed_proxy.add_credentials('name', 'password')
        response, content = testbed_proxy.request(testbed_model.url)
        
        testbed_dict = json.loads(content)
        
        testbed_model.name = testbed_dict['name']
        testbed_model.description = testbed_dict['description']
        testbed_model.organization = testbed_dict['organization']
        response, content = testbed_proxy.request(testbed_dict['nodes'])
        node_list = json.loads(content)
        testbed_model.node_count = len(node_list)
        testbed_model.save()
        
        response, content = testbed_proxy.request(testbed_dict['platforms'])
        
        platform_list = json.loads(content)
        
        for platform in platform_list:
            response, content = testbed_proxy.request(platform['uri'])
            platform_dict = json.loads(content)
            response, content = testbed_proxy.request(testbed_dict['nodes'] + '?platform=' + platform_dict['id'])
            node_list = json.loads(content)
            
            try:
                t2p_list = Testbed2Platform.objects.filter(
                    testbed = testbed_model,
                    platform = Platform.objects.filter(name = platform_dict['name'])[0])
                
                if len(t2p_list) == 0:
                    t2p = Testbed2Platform(testbed = testbed_model, platform = Platform.objects.filter(name = platform_dict['name'])[0], node_count = len(node_list))
                else:
                    t2p = t2p_list[0]
                    t2p.node_count = len(node_list)
                t2p.save()
                    
            except Exception:
                pass
             
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(testbed_model.to_dict()))
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
    

def platform_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        platform_list = [ platform_model.to_dict(head_only = True) for platform_model in Platform.objects.all() ]
        
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
    
def platform_resource_handler(request, platform_id):
    
    allowed_methods = ['GET']
    
    try:
        platform_model = Platform.objects.get(id = platform_id)
    
    except ObjectDoesNotExist:
        
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(platform_model.to_dict()))
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


def project_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        projects = Project.objects.all()
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            projects = projects.filter(name = request.GET['name'])
        
        project_list = [ p.to_dict(head_only = True) for p in projects ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(project_list))
        return response
    
    if request.method == 'POST':
        
        try:
            project_dict = json.loads(request.raw_post_data)

            project_model = Project(
                id = generate_id(),
                name = project_dict['name'],
                description = project_dict['description']
            )
            project_model.save()
            
            # 201
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = project_model.get_absolute_url())
            response['Content-Location'] = build_url(path = project_model.get_absolute_url())
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def project_resource_handler(request, project_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        project_model = Project.objects.get(id = project_id)
    
    except ObjectDoesNotExist:
        
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(project_model.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            project_dict = json.loads(request.raw_post_data)

            project_model.name = project_dict['name']
            project_model.description = project_dict['description']
            
            project_model.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(project_model.to_dict()))
            return response
            
        except None:
            
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        project_model.delete()
        
        # 200
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

def experiment_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        experiments = Experiment.objects.all()
        
        if 'project' in request.GET and not (request.GET['project'] is None):
            experiments = experiments.filter(project = Project.objects.get(id = request.GET['project']))
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            experiments = experiments.filter(name = request.GET['name'])
        
        experiment_list = [ e.to_dict(head_only = True) for e in experiments ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(experiment_list))
        return response
    
    if request.method == 'POST':
        
        try:
            experiment_dict = json.loads(request.raw_post_data)

            experiment_model = Experiment(
                id = generate_id(),
                name = experiment_dict['name'],
                description = experiment_dict['description'],
                project = Project.objects.get(id = experiment_dict['project']))
            experiment_model.save()
            
            # 201
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = experiment_model.get_absolute_url())
            response['Content-Location'] = build_url(path = experiment_model.get_absolute_url())
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def experiment_resource_handler(request, experiment_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        experiment_model = Experiment.objects.get(id = experiment_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(experiment_model.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            experiment_dict = json.loads(request.raw_post_data)

            experiment_model.name = experiment_dict['name']
            experiment_model.description = experiment_dict['description']
            experiment_model.project = Project.objects.get(id = experiment_dict['project'])
            
            experiment_model.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(experiment_model.to_dict()))
            return response
            
        except None:
            
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        experiment_model.delete()
        
        # 200
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    

def property_set_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        property_sets = PropertySet.objects.all()
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            property_sets = property_sets.filter(name = request.GET['name'])
            
        if 'experiment' in request.GET and not (request.GET['experiment'] is None):
            property_sets = property_sets.filter(experiment = Experiment.objects.get(id = request.GET['experiment']))
        
        property_set_list = [ ps.to_dict(head_only = True) for ps in property_sets ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(property_set_list))
        return response
    
    if request.method == 'POST':
        
        try:
            property_set_dict = json.loads(request.raw_post_data)

            property_set = PropertySet(
                id = generate_id(),
                name = property_set_dict['name'],
                experiment = Experiment.objects.get(id = property_set_dict['experiment']),
                platform = Platform.objects.get(id = property_set_dict['platform']),
                node_count = property_set_dict['node_count']
            )
            property_set.save()
            
            for k in range(1, property_set.node_count+1):
                VirtualNode(
                    id = generate_id(),
                    name = 'virtual_node_%d' % k,
                    platform = property_set.platform,
                    experiment = property_set.experiment,
                    property_set = property_set).save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = property_set.get_absolute_url())
            response['Content-Location'] = build_url(path = property_set.get_absolute_url())
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
    
def property_set_resource_handler(request, property_set_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        property_set = PropertySet.objects.get(id = property_set_id)
    
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
        response.write(serialize(property_set.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            property_set_dict = json.loads(request.raw_post_data)

            property_set.name = property_set_dict['name']
            property_set.experiment = Experiment.objects.get(id = property_set_dict['experiment'])
            property_set.platform = Platform.objects.get(id = property_set_dict['platform'])
            property_set.node_count = property_set_dict['node_count']
            
            property_set.save()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(property_set.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        property_set.delete()
        
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    

def virtual_node_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        virtual_nodes = VirtualNode.objects.all()
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            virtual_nodes = virtual_nodes.filter(name = request.GET['name'])
        
        if 'platform' in request.GET and not (request.GET['platform'] is None):
            virtual_nodes = virtual_nodes.filter(platform = Platform.objects.get(id = request.GET['platform']))
            
        if 'property_set' in request.GET and not (request.GET['property_set'] is None):
            virtual_nodes = virtual_nodes.filter(property_set = PropertySet.objects.get(id = request.GET['property_set']))
            
        if 'experiment' in request.GET and not (request.GET['experiment'] is None):
            virtual_nodes = virtual_nodes.filter(experiment = Experiment.objects.get(id = request.GET['experiment']))
            
        if 'n' in request.GET and not (request.GET['n'] is None):
            virtual_nodes = virtual_nodes[:request.GET['n']]
            
        virtual_node_list = [ vn.to_dict(head_only = True) for vn in virtual_nodes ]
        
        logging.warning('NUMBER OF NODES RETURNED: %d' % len(virtual_node_list))
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_node_list))
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
    
def virtual_node_resource_handler(request, virtual_node_id):
    
    allowed_methods = ['GET']
    
    try:
        virtual_node = VirtualNode.objects.get(id = virtual_node_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_node.to_dict()))
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
    
def virtual_nodegroup_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        virtual_nodegroups = VirtualNodeGroup.objects.all()
        
        if 'experiment' in request.GET and not (request.GET['experiment'] is None):
            virtual_nodegroups = virtual_nodegroups.filter(experiment = Experiment.objects.get(id = request.GET['experiment']))
            
        virtual_nodegroup_list = [ vng.to_dict(head_only = True) for vng in virtual_nodegroups ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_nodegroup_list))
        return response
    
    if request.method == 'POST':
        
        try:
            virtual_nodegroup_dict = json.loads(request.raw_post_data)

            virtual_nodegroup = VirtualNodeGroup(
                id = generate_id(),
                name = virtual_nodegroup_dict['name'],
                description = virtual_nodegroup_dict['description'],
                experiment = Experiment.objects.get(id = virtual_nodegroup_dict['experiment']))
            virtual_nodegroup.save()
            
            for virtual_node_id in virtual_nodegroup_dict['virtual_nodes']:
                VirtualNodeGroup2VirtualNode.objects.get_or_create(virtual_nodegroup = virtual_nodegroup, virtual_node = VirtualNode.objects.get(id = virtual_node_id))
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = virtual_nodegroup.get_absolute_url())
            response['Content-Location'] = build_url(path = virtual_nodegroup.get_absolute_url())
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
    
def virtual_nodegroup_resource_handler(request, virtual_nodegroup_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        virtual_nodegroup = VirtualNodeGroup.objects.get(id = virtual_nodegroup_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_nodegroup.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            virtual_nodegroup_dict = json.loads(request.raw_post_data)

            virtual_nodegroup.name = virtual_nodegroup_dict['name']
            virtual_nodegroup.experiment = Experiment.objects.get(id = virtual_nodegroup_dict['experiment'])
            virtual_nodegroup.platform = Platform.objects.get(id = virtual_nodegroup_dict['platform'])
            
            virtual_nodegroup.save()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(virtual_nodegroup.to_dict()))
            return response
            
        except None:
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        virtual_nodegroup.delete()
        
        # 200
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
