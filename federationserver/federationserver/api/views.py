import httplib2
import logging
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from filetransfers.api import prepare_upload, serve_file
from api.models import *
from settings import *
from utils import *
from anyjson import json
from datetime import datetime, timedelta, date
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import time
from google.appengine.ext import blobstore
from google.appengine.api import urlfetch

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
        
        if 'supports_experiment' not in request.GET:
            testbed_list = [ t.to_dict(head_only = True) for t in testbeds ]
        
            # 200
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(testbed_list))
            return response
        
        discovery_matrix = dict()
        discovery_array = dict()
        
        if 'supports_experiment' in request.GET and not (request.GET['supports_experiment'] is None):
            property_sets = PropertySet.objects.filter(experiment = Experiment.objects.get(id = request.GET['supports_experiment']))
        
        elif 'supports_property_set' in request.GET and not (request.GET['supports_property_set'] is None):
            property_sets = [ PropertySet.objects.get(id = request.GET['supports_property_set'])]
            
        else:
            property_sets = []
            
        for testbed in testbeds:
            if testbed.id == 'TWIST':
                discovery_matrix[testbed.id] = dict()
                discovery_array[testbed.id] = True
                for property_set in property_sets:
                    if Testbed2Platform.objects.filter(testbed = testbed, platform=property_set.platform)[0].node_count >= property_set.virtual_node_count:
                        discovery_matrix[testbed.id][property_set.id] = True
                for ps in discovery_matrix[testbed.id]:
                    discovery_array[testbed.id] = discovery_array[testbed.id] and discovery_matrix[testbed.id][ps]
        
        for testbed in testbeds:
            if testbed.id in discovery_array and discovery_array[testbed.id]:
                testbeds = testbeds.filter(id = testbed.id)
                
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
        
        if testbed.id == 'TWIST':
        
            testbed_proxy = httplib2.Http(disable_ssl_certificate_validation=True)
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
            
        except Exception:
            
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
            
        except Exception:
            
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
            virtual_nodegroup.description = virtual_nodegroup_dict['description']
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
            
        except Exception:
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
            response.write(serialize(image.to_dict()))
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
        
        image_dict = image.to_dict()
        upload_url, upload_data = prepare_upload(request, '/experiments/%s/images/%s/upload' % (experiment_id, image_id))
        if image.file:
            image_dict['download'] = build_url(path = '/experiments/%s/images/%s/download' % (experiment_id, image_id))
        image_dict['upload'] = upload_url
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
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
            
        except Exception:
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

    
#def image_resource_in_virtual_node_handler(request, experiment_id, virtual_node_id, image_id):
#    
#    allowed_methods = ['PUT', 'DELETE']
#    
#    try:
#        experiment = Experiment.objects.get(id = experiment_id)
#        node  = VirtualNode.objects.get(id = virtual_node_id)
#        image = Image.objects.get(id = image_id)
#    
#    except ObjectDoesNotExist:
#        # 404
#        response = HttpResponseNotFound()
#        response['Content-Type'] = 'application/json'
#        return response
#        
#    if request.method == 'PUT':
#            
#        node.image = image
#        node.save()
#         
#        # generate response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        return response
#        
#    if request.method == 'DELETE':
#        
#        node.image = None
#        node.save()
#            
#        # generate response
#        response = HttpResponse()
#        response['Content-Type'] = 'application/json'
#        return response
#    
#    if request.method == 'OPTIONS':
#        # 204
#        response = HttpResponse(status=204)
#        response['Allow'] = ', '.join(allowed_methods)
#        del response['Content-Type']
#        return response
#        
#    else:
#        response = HttpResponseNotAllowed(allowed_methods)
#        del response['Content-Type']
#        return response
    
def burn_image_to_virtual_nodegroup_handler(request, experiment_id, virtual_nodegroup_id, image_id):
    
    allowed_methods = ['PUT']
    
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
    
def erase_image_to_virtual_nodegroup_handler(request, experiment_id, virtual_nodegroup_id):
    
    allowed_methods = ['DELETE']
    
    try:
        experiment = Experiment.objects.get(id = experiment_id)
        virtual_nodegroup  = VirtualNodeGroup.objects.get(id = virtual_nodegroup_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
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
            job_uri = testbed.server_url + '/jobs/?'
                    
            if 'for_experiment' in request.GET and not (request.GET['for_experiment'] is None):
                experiment = Experiment.objects.get(id = request.GET['for_experiment'])
                        
            if 'date_from' in request.GET and not (request.GET['date_from'] is None):
                date_from = request.GET['date_from']
                job_uri = job_uri + '&date_from=' + date_from
            
            if 'date_to' in request.GET and not (request.GET['date_to'] is None):
                date_to = request.GET['date_to']
                job_uri = job_uri + '&date_to=' + date_to
                    
            
            testbed_proxy = httplib2.Http(disable_ssl_certificate_validation=True)
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
                    job.datetime_from = utc_string_to_utc_datetime(job_dict['datetime_from'])
                    job.datetime_to = utc_string_to_utc_datetime(job_dict['datetime_to'])
            
            # delete nodes that are not present in the taa database
            # job_id_list = [ job_dict['id'] for job_dict in job_list ]
            # Job.objects.exclude(id__in = job_id_list).delete()
        
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
            
            
            ########## NOW CREATE JOB ################
            
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
            
            testbed_proxy = httplib2.Http(disable_ssl_certificate_validation=True)
            
            logging.info('getting a list of %d of nodes with platform %s...' % (N, PLATFORM))
            response, content = testbed_proxy.request(uri='%s?platform=%s&n=%d' % (testbed.server_url + '/nodes/', PLATFORM, N), method='GET', body='')
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
            uri='%s/jobs/' % (testbed.server_url, )
            logging.info(uri)
            response, content = testbed_proxy.request(uri=uri, method='POST', body=json.dumps(taa_job_dict))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            job_uri = response['content-location']
            logging.info(job_uri)
            
            # create all necessary tasks with nodegroups instead of virtual nodegroups
            
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            
            SERVER_URL = testbed.server_url
            PLATFORM = 'TmoteSky'
            JOB_URI = job_uri
        
            SINK_NODE_ID = 12
            INTERFERER_NODE_ID_1 = 187
            INTERFERER_NODE_ID_2 = 93
            
            DESCRIPTION = 'CONET 3Y REVIEW - PLEASE DO NOT DELETE'

            # GETTING THE TESTBED
    
            logging.info('getting the testbed resource...')
            response, content = testbed_proxy.request(uri=SERVER_URL, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            testbed_dict = json.loads(content)
            logging.debug(testbed_dict)
            
            # GETTING THE JOB (INCLUDING NODES)
            
            logging.info('getting the information about the created job...')
            response, content = testbed_proxy.request(uri=JOB_URI, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            job_dict = json.loads(content)
            logging.debug(job_dict)
            
            assert len(job_dict['nodes']) == 96
            
            # GETTING THE NODES AND CREATING THE NODEGROUP ALL
            
            logging.info('getting the nodes for nodegroup including all nodes %s...' % (PLATFORM, ))
            response, content = testbed_proxy.request(uri='%s?platform=%s' % (testbed_dict['nodes'], PLATFORM), method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            node_list_all = json.loads(content)
            logging.debug(node_list_all)
            assert len(node_list_all) == 96
                
            nodegroup_dict_all = {
                'name' : 'subscriber',
                'description' : DESCRIPTION,
                'nodes' : [ n['id'] for n in node_list_all ],
                'job' : job_dict['id']
            }
            
            logging.info('creating the nodegroup for all nodes %s...' % (PLATFORM, ))    
            response, content = testbed_proxy.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_all))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_uri_all = response['content-location']
            logging.debug(nodegroup_uri_all)
            
            logging.info('getting the information about the created nodegroup all...')
            response, content = testbed_proxy.request(uri=nodegroup_uri_all, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_dict_all = json.loads(content)
            logging.debug(nodegroup_dict_all)
            assert len(nodegroup_dict_all['nodes']) == 96
            
            ngA = nodegroup_dict_all['id'] ###############################################################################################################################

            
            # GETTING THE NODES AND CREATING THE NODEGROUP SUBSCRIBER
            
            logging.info('getting the nodes for nodegroup subscriber (1 node)...')
            response, content = testbed_proxy.request(uri='%s?native_id=%d' % (testbed_dict['nodes'], SINK_NODE_ID), method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            node_list_subscriber = json.loads(content)
            logging.debug(node_list_subscriber)
            assert len(node_list_subscriber) == 1
                
            nodegroup_dict_subscriber = {
                'name' : 'subscriber',
                'description' : DESCRIPTION,
                'nodes' : [ n['id'] for n in node_list_subscriber ],
                'job' : job_dict['id']
            }
            
            logging.info('creating the nodegroup for subscriber...')    
            response, content = testbed_proxy.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_subscriber))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_uri_subscriber = response['content-location']
            logging.debug(nodegroup_uri_subscriber)
            
            logging.info('getting the information about the created nodegroup subscriber...')
            response, content = testbed_proxy.request(uri=nodegroup_uri_subscriber, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_dict_subscriber = json.loads(content)
            logging.debug(nodegroup_dict_subscriber)
            assert len(nodegroup_dict_subscriber['nodes']) == 1
            
            ngS = nodegroup_dict_subscriber['id'] ###############################################################################################################################
            
            # GETTING THE NODES AND CREATING THE NODEGROUP PUBLISHERS
            
            logging.info('getting the nodes for nodegroup publishers (93 nodes)...')
            # node_blacklist = [ 59, 60, 274, 275, 62, 64, 276, 277, 171, 174, 278, 279]
            response, content = testbed_proxy.request(uri='%s?platform=%s&native_id__not_in=%d,%d,%d' % (testbed_dict['nodes'], PLATFORM, SINK_NODE_ID, INTERFERER_NODE_ID_1, INTERFERER_NODE_ID_2), method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            node_list_publishers = json.loads(content)
            logging.debug(node_list_publishers)
            logging.debug(len(node_list_publishers))
            assert len(node_list_publishers) == 93
                
            nodegroup_dict_publishers = {
                'name' : 'publishers',
                'description' : DESCRIPTION,
                'nodes' : [ n['id'] for n in node_list_publishers ],
                'job' : job_dict['id']
            }
            
            logging.info('creating a nodegroup publishers...')    
            response, content = testbed_proxy.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_publishers))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_uri_publishers = response['content-location']
            logging.debug(nodegroup_uri_publishers)
            
            logging.info('getting the information about the created nodegroup publishers...')
            response, content = testbed_proxy.request(uri=nodegroup_uri_publishers, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_dict_publishers = json.loads(content)
            logging.debug(nodegroup_dict_publishers)
            assert len(nodegroup_dict_publishers['nodes']) == 93
            
            ngP = nodegroup_dict_publishers['id'] ###############################################################################################################################
            
            # GETTING THE NODES AND CREATING THE NODEGROUP INTERFERERS
            
            logging.info('getting the nodes for nodegroup interferers (2 nodes)...')
            response, content = testbed_proxy.request(uri='%s?native_id__in=%d,%d' % (testbed_dict['nodes'], INTERFERER_NODE_ID_1, INTERFERER_NODE_ID_2), method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            node_list_interferers = json.loads(content)
            logging.debug(node_list_interferers)
            assert len(node_list_interferers) == 2
                
            nodegroup_dict_interferers = {
                'name' : 'interferers',
                'description' : DESCRIPTION,
                'nodes' : [ n['id'] for n in node_list_interferers ],
                'job' : job_dict['id']
            }
            
            logging.info('creating a nodegroup interferers...')    
            response, content = testbed_proxy.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_interferers))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_uri_interferers = response['content-location']
            logging.debug(nodegroup_uri_interferers)
            
            logging.info('getting the information about the created nodegroup interferers...')
            response, content = testbed_proxy.request(uri=nodegroup_uri_interferers, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            nodegroup_dict_interferers = json.loads(content)
            logging.debug(nodegroup_dict_interferers)
            assert len(nodegroup_dict_interferers['nodes']) == 2
            
            ngI = nodegroup_dict_interferers['id'] ###############################################################################################################################
            
            # UPLOADING THE IMAGE FOR SUBSCRIBER
            
            image_dict_subscriber = {
                    'name' : 'image for subscriber',
                    'description' : DESCRIPTION,
                }
                
            logging.info('creating a new image resource...')
            response, content = testbed_proxy.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_subscriber))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            image_uri_subscriber = response['content-location']
            logging.debug(image_uri_subscriber)
            
            logging.info('getting the information about the image for subscriber...')
            response, content = testbed_proxy.request(uri=image_uri_subscriber, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            image_dict_subscriber= json.loads(content)
            logging.debug(image_dict_subscriber)
        
            logging.info('uploading the actual image file...')
            image = Image.objects.filter(experiment = experiment).filter(name = 'SUBSCRIBER')[0]
            blob_key = image.file.file.blobstore_info.key()
            blob_info = blobstore.BlobInfo(blob_key)
            content = blobstore.fetch_data(blob_info, 0, blobstore.MAX_BLOB_FETCH_SIZE-1) # file content
            params = []
            params.append(MultipartParam('imagefile', filename=image.file.name, filetype='application/octet-stream', value=content))
            
            datagen, headers = multipart_encode(params)
            data = str().join(datagen)
            result = urlfetch.fetch(url=image_dict_subscriber['upload'], payload=data, method=urlfetch.POST, headers=headers, deadline=10)
            logging.info('%d' % (result.status_code))
            
            imS = image_dict_subscriber['id'] ################################################################################################################################
            
            # UPLOADING THE IMAGE FOR PUBLISHERS
            
            image_dict_publishers = {
                    'name' : 'image for publishers',
                    'description' : DESCRIPTION,
                }
                
            logging.info('creating a new image resource...')
            response, content = testbed_proxy.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_publishers))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            image_uri_publishers = response['content-location']
            logging.debug(image_uri_publishers)
            
            logging.info('getting the information about the image for publishers...')
            response, content = testbed_proxy.request(uri=image_uri_publishers, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            image_dict_publishers= json.loads(content)
            logging.debug(image_dict_publishers)
            
            logging.info('uploading the actual image file...')
            image = Image.objects.filter(experiment = experiment).filter(name = 'PUBLISHER')[0]
            blob_key = image.file.file.blobstore_info.key()
            blob_info = blobstore.BlobInfo(blob_key)
            content = blobstore.fetch_data(blob_info, 0, blobstore.MAX_BLOB_FETCH_SIZE-1) # file content
            params = []
            params.append(MultipartParam('imagefile', filename=image.file.name, filetype='application/octet-stream', value=content))
            
            datagen, headers = multipart_encode(params)
            data = str().join(datagen)
            result = urlfetch.fetch(url=image_dict_publishers['upload'], payload=data, method=urlfetch.POST, headers=headers, deadline=10)
            logging.info('%d' % (result.status_code))
            
            imP = image_dict_publishers['id'] ################################################################################################################################
            
            # UPLOADING THE IMAGE FOR INTERFERERS
            
            image_dict_interferers = {
                    'name' : 'image for interferers',
                    'description' : DESCRIPTION,
                }
                
            logging.info('creating a new image resource...')
            response, content = testbed_proxy.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_interferers))
            assert response.status == 201
            logging.info('%d %s' % (response.status, response.reason))
            image_uri_interferers = response['content-location']
            logging.debug(image_uri_interferers)
            
            logging.info('getting the information about the image for interferers...')
            response, content = testbed_proxy.request(uri=image_uri_interferers, method='GET', body='')
            assert response.status == 200
            logging.info('%d %s' % (response.status, response.reason))
            image_dict_interferers= json.loads(content)
            logging.debug(image_dict_interferers)
            
            logging.info('uploading the actual image file...')
            image = Image.objects.filter(experiment = experiment).filter(name = 'INTERFERER')[0]
            blob_key = image.file.file.blobstore_info.key()
            blob_info = blobstore.BlobInfo(blob_key)
            content = blobstore.fetch_data(blob_info, 0, blobstore.MAX_BLOB_FETCH_SIZE-1) # file content
            params = []
            params.append(MultipartParam('imagefile', filename=image.file.name, filetype='application/octet-stream', value=content))
            
            datagen, headers = multipart_encode(params)
            data = str().join(datagen)
            result = urlfetch.fetch(url=image_dict_interferers['upload'], payload=data, method=urlfetch.POST, headers=headers, deadline=10)
            logging.info('%d' % (result.status_code))
            
            imI = image_dict_interferers['id'] ################################################################################################################################
            
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            #####################################################################################################
            
            ########## NOW CREATE TASKS ##############
            
            virtual_task = VirtualTask.objects.filter(experiment = job.experiment).filter(step = 1)[0]
            target = '%s/nodegroups/%s/image' % (SERVER_URL, ngA)
            Task(id = generate_id(), job = job, virtual_task = virtual_task, target = target).save()
            
            virtual_task = VirtualTask.objects.filter(experiment = job.experiment).filter(step = 2)[0]
            target = '%s/nodegroups/%s/image/%s' % (SERVER_URL, ngS, imS)
            Task(id = generate_id(), job = job, virtual_task = virtual_task, target = target).save()
            
            virtual_task = VirtualTask.objects.filter(experiment = job.experiment).filter(step = 3)[0]
            target = '%s/nodegroups/%s/image/%s' % (SERVER_URL, ngP, imP)
            Task(id = generate_id(), job = job, virtual_task = virtual_task, target = target).save()
            
            virtual_task = VirtualTask.objects.filter(experiment = job.experiment).filter(step = 4)[0]
            target = '%s/nodegroups/%s/image/%s' % (SERVER_URL, ngI, imI)
            Task(id = generate_id(), job = job, virtual_task = virtual_task, target = target).save()
            
            virtual_task = VirtualTask.objects.filter(experiment = job.experiment).filter(step = 5)[0]
            target = '%s/nodegroups/%s/image' % (SERVER_URL, ngI)
            Task(id = generate_id(), job = job, virtual_task = virtual_task, target = target).save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = job.get_absolute_url())
            response['Content-Location'] = build_url(path = job.get_absolute_url())
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
    


def task_collection_handler(request, job_id):

    allowed_methods = ['GET']
    
    try:
        job = Job.objects.get(id = job_id)
    
    except ObjectDoesNotExist:
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':

        tasks = Task.objects.filter(job = job)

        if 'name' in request.GET and not (request.GET['name'] is None):
            tasks = tasks.filter(name = request.GET['name'])

        task_list = [ t.to_dict(head_only = True) for t in tasks ]
        
        ordered_task_list = sorted(task_list, key=lambda k: k['step'])

        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(ordered_task_list))
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

def task_resource_handler(request, job_id, task_id):

    allowed_methods = ['GET']

    try:
        job = Job.objects.get(id = job_id)
        task = Task.objects.get(id = task_id)

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
        response.write(serialize(task.to_dict()))
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def run_task_resource_handler(request, job_id, task_id):

    allowed_methods = ['PUT']

    try:
        job = Job.objects.get(id = job_id)
        task = Task.objects.get(id = task_id)

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

    if request.method == 'PUT':
        
        # esegui il task
        
        ##########################################################################
        ##########################################################################
        ############# THIS CAN ONLY BE EXECUTED ON REAL NODES!! ##################
        ##########################################################################
        ##########################################################################
        
        # TO DO: USE TASK QUEUE + URLFETCH!
          
        testbed_proxy = httplib2.Http(disable_ssl_certificate_validation=True)
        
        logging.info('executing task')
        headers = {'Content-Length' : '0'}
        testbed_response, content = testbed_proxy.request(uri=task.target, method=task.virtual_task.method, body='', headers=headers)
        logging.debug(testbed_response)
        assert testbed_response.status == 202
        logging.info('%d %s' % (testbed_response.status, testbed_response.reason))
        
        logging.info('DONE!')
        
        # 200
        response = HttpResponse(status=202)
        response['Content-Type'] = 'application/json'
        response['Location'] = testbed_response['location']
        return response

    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response

