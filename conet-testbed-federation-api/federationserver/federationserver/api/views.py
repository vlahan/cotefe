import logging
import xmlrpclib
from datetime import datetime
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from federationserver.api.models import *
from federationserver.config import *
from federationserver.utils import *
from django.contrib.auth.models import UserManager

# FEDERATION
def federation_resource_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':
        resource_model = Federation.objects.all()[0]
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(resource_model.to_dict()))
        return response
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
# PROJECT
def project_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':

        # gets all the platforms from this database
        collection_queryset = Project.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict(head_only = True))
        
        # generating response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'POST':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model = Project(
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
            # generate response
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def project_resource_handler(request, project_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource_model = Project.objects.get(uid = project_id)
    
    except ObjectDoesNotExist:
        # response = HttpResponseNotFound()
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':
        # generate response
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
            # generate response
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
    
def experiment_collection_in_project_handler(request, project_id):
    
    allowed_methods = ['GET']
    
    try:
        project_model = Project.objects.get(uid = project_id)
    
    except ObjectDoesNotExist:
        # response = HttpResponseNotFound()
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':

        # gets all the platforms from this database
        collection_queryset = Experiment.objects.filter(project = project_model)
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict(head_only = True))
        
        # generating response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
# EXPERIMENT
def experiment_collection_handler(request):
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':

        # gets all the platforms from this database
        collection_queryset = Experiment.objects.all()
        collection_list = list()
        for resource_model in collection_queryset:
            collection_list.append(resource_model.to_dict(head_only = True))
        
        # generating response
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(collection_list))
        return response
    
    if request.method == 'POST':
        
        resource_json = request.raw_post_data
        
        try:
            resource_dict = json.loads(resource_json)

            resource_model = Experiment(
                uid = generate_uid(),
                name = resource_dict['name'],
                description = resource_dict['description'],
                project = Project.objects.get(uid = resource_dict['project']))
            resource_model.save()
            
            # generate response
            response = HttpResponse(status=201)
            response['Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Location'] = build_url(path = resource_model.get_absolute_url())
            response['Content-Type'] = 'application/json'
            return response
        except Exception:
            # generate response
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
    else:
        response = HttpResponseNotAllowed(allowed_methods)
        del response['Content-Type']
        return response
    
def experiment_resource_handler(request, experiment_id):
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource_model = Experiment.objects.get(uid = experiment_id)
    
    except ObjectDoesNotExist:
        # response = HttpResponseNotFound()
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response
        
    if request.method == 'OPTIONS':
        # generating response
        response = HttpResponse(status=204)
        response['Allow'] = ', '.join(allowed_methods)
        del response['Content-Type']
        return response
    
    if request.method == 'GET':
        # generate response
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
            resource_model.project = Project.objects.get(uid = resource_dict['project'])
            
            resource_model.save()
            
            # generate response
            response = HttpResponse()
            response['Content-Type'] = 'application/json'
            response.write(serialize(resource_model.to_dict()))
            return response
            
        except Exception:
            # generate response
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