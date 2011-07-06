import logging
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from api.models import *
from settings import *
from utils import *

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
    
def project_resource_handler(request, project_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        project_model = Project.objects.get(uid = project_uid)
    
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
    
def experiment_collection_in_project_handler(request, project_uid):
    
    allowed_methods = ['GET']
    
    try:
        project_model = Project.objects.get(uid = project_uid)
    
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
    
def experiment_resource_handler(request, experiment_uid):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        experiment_model = Experiment.objects.get(uid = experiment_uid)
    
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
            experiment_model.project = Project.objects.get(uid = experiment_dict['project'])
            
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