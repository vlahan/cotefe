import httplib2
import logging
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from filetransfers.api import prepare_upload, serve_file
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
        
        testbeds = Testbed.objects.all()
        
        discovery_matrix = dict()
        discovery_array = dict()
        
        if 'supports_experiment' in request.GET and not (request.GET['supports_experiment'] is None):
            property_sets = PropertySet.objects.filter(experiment = Experiment.objects.get(id = request.GET['supports_experiment']))
        
        elif 'supports_property_set' in request.GET and not (request.GET['supports_property_set'] is None):
            property_sets = [ PropertySet.objects.get(id = request.GET['supports_property_set'])]
            
        else:
            property_sets = []
            
        for testbed in testbeds:
            discovery_matrix[testbed.id] = dict()
            discovery_array[testbed.id] = True
            for property_set in property_sets:
                discovery_matrix[testbed.id][property_set.id] = Testbed2Platform.objects.filter(testbed = testbed, platform=property_set.platform)[0].node_count >= property_set.virtual_node_count
            for ps in discovery_matrix[testbed.id]:
                discovery_array[testbed.id] = discovery_array[testbed.id] and discovery_matrix[testbed.id][ps]
        
        for t in testbeds:
            if not discovery_array[t.id]:
                testbeds = testbeds.exclude(id = t.id)
                
        testbed_list = [ t.to_dict(head_only = True) for t in testbeds ]
        
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
        testbed = Testbed.objects.get(id = testbed_id)
    
    except ObjectDoesNotExist:
        
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        testbed_proxy = httplib2.Http()
        # testbed_proxy.add_credentials('name', 'password')
        response, content = testbed_proxy.request(uri=testbed.server_url, method='GET', body='')
        assert response.status == 200
        testbed_dict = json.loads(content)
        
        testbed.name = testbed_dict['name']
        testbed.description = testbed_dict['description']
        testbed.organization = testbed_dict['organization']
        response, content = testbed_proxy.request(testbed_dict['nodes'])
        node_list = json.loads(content)
        testbed.node_count = len(node_list)
        testbed.save()
        
        for platform in Platform.objects.all():
            response, content = testbed_proxy.request(uri='%s?platform=%s' % (testbed_dict['nodes'], platform.id), method='GET', body='')
            assert response.status == 200
            node_list = json.loads(content)
            t2p, created = Testbed2Platform.objects.get_or_create(
                testbed = testbed,
                platform = platform,
                defaults = {
                    'node_count': len(node_list)
                }
            )
            if not created:
                t2p.node_count = len(node_list)
                t2p.save()
             
        # 200
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
        # 405
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    

def platform_collection_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        platforms = Platform.objects.all()
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            platforms = platforms.filter(name = request.GET['name'])
        
        platform_list = [ p.to_dict(head_only = True) for p in platforms ]
        
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

            experiment = Experiment(
                id = generate_id(),
                name = experiment_dict['name'],
                description = experiment_dict['description'],
                project = Project.objects.get(id = experiment_dict['project'])
            )
            experiment.save()
            
            # 201
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = experiment.get_absolute_url())
            response['Content-Location'] = build_url(path = experiment.get_absolute_url())
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
        experiment = Experiment.objects.get(id = experiment_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(experiment.to_dict()))
        return response
    
    if request.method == 'PUT':
        
        try:
            experiment_dict = json.loads(request.raw_post_data)

            experiment.name = experiment_dict['name']
            experiment.description = experiment_dict['description']
            experiment.project = Project.objects.get(id = experiment_dict['project'])
            
            experiment.save()
            
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(experiment.to_dict()))
            return response
            
        except None:
            
            # 400
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    if request.method == 'DELETE':
        
        experiment.delete()
        
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
    

def property_set_collection_handler(request, experiment_id):
    
    allowed_methods = ['GET', 'POST']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        property_sets = PropertySet.objects.filter(experiment = experiment)
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            property_sets = property_sets.filter(name = request.GET['name'])
        
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
                description = property_set_dict['description'],
                experiment = experiment,
                platform = Platform.objects.get(id = property_set_dict['platform']),
                virtual_node_count = property_set_dict['virtual_node_count']
            )
            property_set.save()
            
            for k in range(1, property_set.virtual_node_count+1):
                VirtualNode(
                    id = generate_id(),
                    name = 'virtual_node_%d' % k,
                    platform = property_set.platform,
                    experiment = property_set.experiment,
                    property_set = property_set).save()
            
            # 201
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
    
def property_set_resource_handler(request, experiment_id, property_set_id):
    
    allowed_methods = ['GET', 'DELETE']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        property_set = PropertySet.objects.get(id = property_set_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(property_set.to_dict()))
        return response
        
    if request.method == 'DELETE':
        
        property_set.delete()
        
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
    

def virtual_node_collection_handler(request, experiment_id):
    
    allowed_methods = ['GET']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        virtual_nodes = VirtualNode.objects.filter(experiment = experiment)
        # virtual_nodes = VirtualNode.objects.all().order_by('property_set', 'name')
        
        if 'name' in request.GET and not (request.GET['name'] is None):
            virtual_nodes = virtual_nodes.filter(name = request.GET['name'])
        
        if 'platform' in request.GET and not (request.GET['platform'] is None):
            virtual_nodes = virtual_nodes.filter(platform = Platform.objects.get(id = request.GET['platform']))
            
        if 'property_set' in request.GET and not (request.GET['property_set'] is None):
            virtual_nodes = virtual_nodes.filter(property_set = PropertySet.objects.get(id = request.GET['property_set']))
            
        if 'n' in request.GET and not (request.GET['n'] is None):
            if len(virtual_nodes) >= request.GET['n']:
                virtual_nodes = virtual_nodes[:request.GET['n']]
            else:
                # 404
                response = HttpResponseNotFound()
                response['Content-Type'] = 'application/json'
                return response
                
        virtual_node_list = [ vn.to_dict(head_only = True) for vn in virtual_nodes ]
                
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
    
def virtual_node_resource_handler(request, experiment_id, virtual_node_id):
    
    allowed_methods = ['GET']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
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
    
def virtual_nodegroup_collection_handler(request, experiment_id):
    
    allowed_methods = ['GET', 'POST']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        virtual_nodegroups = VirtualNodeGroup.objects.filter(experiment = experiment)
            
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
                experiment = experiment)
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
    
def virtual_nodegroup_resource_handler(request, experiment_id, virtual_nodegroup_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        virtual_nodegroup = VirtualNodeGroup.objects.get(id = virtual_nodegroup_id)
        experiment = Experiment.objects.get(id = experiment_id)

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
            virtual_nodegroup.name = virtual_nodegroup_dict['description']
            virtual_nodegroup.experiment = Experiment.objects.get(id = virtual_nodegroup_dict['experiment'])
            virtual_nodegroup.save()
            
            for vng2vn in VirtualNodeGroup2VirtualNode.objects.filter(virtual_nodegroup = virtual_nodegroup):
                vng2vn.delete()
            
            for virtual_node_id in virtual_nodegroup_dict['virtual_nodes']:
                VirtualNodeGroup2VirtualNode.objects.get_or_create(virtual_nodegroup = virtual_nodegroup, virtual_node = VirtualNode.objects.get(id = virtual_node_id))
            
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
        for vng2vn in VirtualNodeGroup2VirtualNode.objects.filter(virtual_nodegroup = virtual_nodegroup):
                vng2vn.delete()
        
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

def image_collection_handler(request, experiment_id):
    
    allowed_methods = ['GET', 'POST']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        images = Image.objects.filter(experiment = experiment)
        
        image_list = [ i.to_dict(head_only = True) for i in images ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(image_list))
        return response
    
    if request.method == 'POST':
                
        try:
            image_dict = json.loads(request.raw_post_data)
            
            image = Image(
                id = generate_id(),
                name = image_dict['name'],
                description = image_dict['description'],
                experiment = experiment,
            )
            
            image.save()
            
            # 201
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = image.get_absolute_url())
            response['Content-Location'] = build_url(path = image.get_absolute_url())
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
    
def image_resource_handler(request, experiment_id, image_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        image = Image.objects.get(id = image_id)
        experiment = Experiment.objects.get(id = experiment_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        
        image_dict = image.to_dict()
        upload_url, upload_data = prepare_upload(request, '/experiments/%s/images/%s/upload' % (experiment_id, image_id))
        image_dict['upload'] = upload_url
        image_dict['download'] = build_url(path = '/experiments/%s/images/%s/download' % (experiment_id, image_id))
        response.write(serialize(image_dict))
        
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


def imagefile_upload_handler(request, experiment_id, image_id):
    
    allowed_methods = ['POST']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
      
    if request.method == 'POST':
                
        try:       
            imagefile = request.FILES['imagefile']
            
            image.file = imagefile            
            image.save()
            
            # 200
            response = HttpResponseRedirect('/experiments/%s/images/%s' % (experiment_id, image_id))
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
    
def imagefile_download_handler(request, experiment_id, image_id):
    
    allowed_methods = ['GET']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
      
    if request.method == 'GET':
                
        return serve_file(request, image.file, save_as=True, content_type='application/octet-stream')
        
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

def virtual_task_collection_handler(request, experiment_id):

    allowed_methods = ['GET', 'POST']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':

        virtual_tasks = VirtualTask.objects.filter(experiment = experiment).order_by('step')

        if 'name' in request.GET and not (request.GET['name'] is None):
            virtual_tasks = virtual_tasks.filter(name = request.GET['name'])

        virtual_task_list = [ vt.to_dict(head_only = True) for vt in virtual_tasks ]

        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_task_list))
        return response

    if request.method == 'POST':

        try:
            virtual_task_dict = json.loads(request.raw_post_data)

            virtual_task = VirtualTask(
                id = generate_id(),
                name = virtual_task_dict['name'],
                description = virtual_task_dict['description'],
                step = virtual_task_dict['step'],
                experiment = experiment,
                method = virtual_task_dict['method'],
                target = virtual_task_dict['target']
            )
            virtual_task.save()

            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = virtual_task.get_absolute_url())
            response['Content-Location'] = build_url(path = virtual_task.get_absolute_url())
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

def virtual_task_resource_handler(request, experiment_id, virtual_task_id):

    allowed_methods = ['GET', 'PUT', 'DELETE']

    try:
        experiment = Experiment.objects.get(id = experiment_id)
        virtual_task = VirtualTask.objects.get(id = virtual_task_id)

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
        response.write(serialize(virtual_task.to_dict()))
        return response
        
    if request.method == 'PUT':
        
        virtual_task_dict = json.loads(request.raw_post_data)
        
        virtual_task.name = virtual_task_dict['name']
        virtual_task.description = virtual_task_dict['description']
        virtual_task.experiment = Experiment.objects.get(id = virtual_task_dict['experiment'])
        virtual_task.method = virtual_task_dict['method']
        virtual_task.target = virtual_task_dict['target']
        virtual_task.save()
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(virtual_task.to_dict()))
        return response

    if request.method == 'DELETE':

        virtual_task.delete()

        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

    
def image_resource_in_virtual_node_handler(request, experiment_id, virtual_node_id, image_id):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        node  = VirtualNode.objects.get(id = virtual_node_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'PUT':
            
        node.image = image
        node.save()
         
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'DELETE':
        
        node.image = None
        node.save()
            
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
    
def image_resource_in_virtual_nodegroup_handler(request, experiment_id, virtual_nodegroup_id, image_id):
    
    allowed_methods = ['PUT', 'DELETE']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        virtual_nodegroup  = VirtualNodeGroup.objects.get(id = virtual_nodegroup_id)
        image = Image.objects.get(id = image_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response    
        
    if request.method == 'PUT':
            
        virtual_nodegroup.image = image
        virtual_nodegroup.save()
        
        for vng2vn in VirtualNodeGroup2VirtualNode.objects.filter(virtual_nodegroup = virtual_nodegroup):
            vng2vn.virtual_node.image = image
            vng2vn.virtual_node.save()
         
        # generate response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'DELETE':
        
        virtual_nodegroup.image = None
        virtual_nodegroup.save()
        
        for vng2vn in VirtualNodeGroup2VirtualNode.objects.filter(virtual_nodegroup = virtual_nodegroup):
            vng2vn.node.image = None
            vng2vn.node.save()
        
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
    
def job_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        if 'testbed' in request.GET and not (request.GET['testbed'] is None):
            testbed = Testbed.objects.get(id = request.GET['testbed'])
            job_uri = testbed.server_url + 'jobs/?'
            
        if 'for_experiment' in request.GET and not (request.GET['for_experiment'] is None):
            experiment = Experiment.objects.get(id = request.GET['for_experiment'])
            
        if 'date_from' in request.GET and not (request.GET['date_from'] is None):
            date_from = request.GET['date_from']
            job_uri = job_uri + '&date_from=' + date_from
            
        if 'date_to' in request.GET and not (request.GET['date_to'] is None):
            date_to = request.GET['date_to']
            job_uri = job_uri + '&date_to=' + date_to
        
        testbed_proxy = httplib2.Http()
        # testbed_proxy.add_credentials('name', 'password')
        response, content = testbed_proxy.request(uri=job_uri, method='GET', body='')
        assert response.status == 200
        job_list = json.loads(content)
        
        for job_item in job_list:
            response, content = testbed_proxy.request(uri=job_item['uri'], method='GET', body='')
            assert response.status == 200
            job_dict = json.loads(content)
            job, created = Job.objects.get_or_create(
                id = job_dict['id'],
                defaults = {
                    'name' : job_dict['name'],
                    'description' : job_dict['description'],
                    'datetime_from' : utc_string_to_utc_datetime(job_dict['datetime_from']),
                    'datetime_to' : utc_string_to_utc_datetime(job_dict['datetime_to']),
                    'testbed' : testbed
                }
            )
            if not created:
                job.name = job_dict['name']
                job.description = job_dict['description']
        
        # delete nodes that are not present in the taa database
        job_id_list = [ job_dict['id'] for job_dict in job_list ]
        Job.objects.exclude(id__in = job_id_list).delete()
        
        jobs = Job.objects.all().order_by('datetime_from')
        job_list = [ j.to_dict(head_only = True) for j in jobs ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(job_list))
        return response
    
    if request.method == 'POST':
        
        try:
            job_dict = json.loads(request.raw_post_data)
            
            testbed = Testbed.objects.get(id = job_dict['testbed'])
            experiment = Experiment.objects.get(id = job_dict['experiment'])
            
            job = Job(
                id = generate_id(),
                name = job_dict['name'],
                description = job_dict['description'],
                datetime_from = utc_string_to_utc_datetime(job_dict['datetime_from']),
                datetime_to = utc_string_to_utc_datetime(job_dict['datetime_to']),
                testbed = testbed,
                experiment = experiment
            )
            job.save()
            
            N = 96
            PLATFORM = 'TmoteSky'
            
            testbed_proxy = httplib2.Http()
            
            logging.info('getting a list of %d of nodes with platform %s...' % (N, PLATFORM))
            response, content = testbed_proxy.request(uri='%s?platform=%s&n=%d' % (testbed.server_url + 'nodes/', PLATFORM, N), method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            node_list = json.loads(content)
            logging.debug(node_list)
        
            taa_job_dict = {
                'name' : job_dict['name'],
                'description' : job_dict['description'],
                'nodes' : [ n['id'] for n in node_list ],
                'datetime_from' : job_dict['datetime_from'],
                'datetime_to' : job_dict['datetime_to'],
            }
            
            logging.debug(taa_job_dict)
            
            logging.info('creating a new job..')    
            response, content = testbed_proxy.request(uri=testbed.server_url + 'jobs/', method='POST', body=json.dumps(taa_job_dict))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            job_uri = response['content-location']
            logging.info(job_uri)
            
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
    
    allowed_methods = ['GET']
    
    try:
        job = Job.objects.get(id = job_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(job.to_dict()))
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

