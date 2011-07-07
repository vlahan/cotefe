import httplib2
import logging
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from federationserver.api.models import *
from federationserver.settings import *
from federationserver.utils import *

# FEDERATION
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
    
# TESTBED
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
    
# PLATFORM
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

# PROJECT
def project_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        project_list = [ project_model.to_dict(head_only = True) for project_model in Project.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(project_list))
        return response
    
    if request.method == 'POST':
        
        try:
            project_dict = json.loads(request.raw_post_data)

            project_model = Project(
                uid = generate_uid(),
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
    
def experiment_collection_in_project_handler(request, project_id):
    
    allowed_methods = ['GET']
    
    try:
        project_model = Project.objects.get(uid = project_id)
    
    except ObjectDoesNotExist:
        
        # 404
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
    
    if request.method == 'GET':
        
        experiment_list = [ experiment_model.to_dict(head_only = True) for experiment_model in Experiment.objects.filter(project = project_model) ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(experiment_list))
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
    
# EXPERIMENT
def experiment_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        experiment_list = [ experiment_model.to_dict(head_only = True) for experiment_model in Experiment.objects.all() ]
        
        # 200
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(experiment_list))
        return response
    
    if request.method == 'POST':
        
        try:
            experiment_dict = json.loads(request.raw_post_data)

            experiment_model = Experiment(
                uid = generate_uid(),
                name = experiment_dict['name'],
                description = experiment_dict['description'],
                project = Project.objects.get(uid = experiment_dict['project']))
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
        experiment_model = Experiment.objects.get(uid = experiment_id)
    
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
    
# PROPERTY SET
def property_set_collection_handler(request):
    pass

def property_set_resource_handler(request, property_set_id):
    pass