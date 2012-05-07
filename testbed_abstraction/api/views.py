import json

from django.http import HttpResponse, HttpResponseNotAllowed

from testbed_abstraction import config, utils
from api.models import *

model_by_url = dict()
model_by_url['nodes'] = Node
model_by_url['jobs'] = Job
model_by_url['images'] = Image
model_by_url['users'] = User

def root_handler(request):
    
    allowed_methods = ['GET']
    
    if request.method == 'GET':
        
        resource = OrderedDict()
        resource['uri'] = config.SERVER_URL+'/'
        resource['media_type'] = config.MEDIA_TYPE
        resource['name'] = config.TESTBED_NAME
        resource['organization'] = config.TESTBED_ORGANIZATION
        resource['city'] = config.TESTBED_CITY
        resource['country'] = config.TESTBED_COUNTRY
        resource['nodes'] = config.SERVER_URL+'/nodes/'
        resource['jobs'] = config.SERVER_URL+'/jobs/'
        resource['images'] = config.SERVER_URL+'/images/'
        resource['users'] = config.SERVER_URL+'/users/'
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(resource))
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
    
    
def collection_handler(request, resource_url_path):
    
    Model = model_by_url[resource_url_path]
    
    allowed_methods = ['GET', 'POST']
    
    if request.method == 'GET':
        
        collection = Model.objects.all()

        collection = [ resource.to_dict(head_only = True) for resource in collection ]
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(collection))
        return response
    
    if request.method == 'POST':
        
        try:
            resource_dict = json.loads(request.raw_post_data)
        except Exception:
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
        
        resource = Model()
        resource.name = resource_dict['name']
        resource.save()
        
        response = HttpResponse(status=201)
        response['Location'] = resource.get_absolute_url()
        response['Content-Location'] = resource.get_absolute_url()
        response['Content-Type'] = 'application/json'
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

def resource_handler(request, resource_url_path, resource_id):
    
    Model = model_by_url[resource_url_path]
    
    allowed_methods = ['GET', 'PUT', 'DELETE']
    
    try:
        resource = Model.objects.get(id = resource_id)
    
    except ObjectDoesNotExist:
        response = HttpResponseNotFound()
        response['Content-Type'] = 'application/json'
        return response

    if request.method == 'GET':
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(utils.serialize(resource.to_dict()))
        return response
    
    if request.method == 'PUT':

        try:
            resource_dict = json.loads(request.raw_post_data)
            
        except Exception:
            response = HttpResponseBadRequest()
            response['Content-Type'] = 'application/json'
            return response
            
        resource.name = resource_dict['name']
        resource.save()

        response = HttpResponse()
        response['Content-Type'] = 'application/json'
        response.write(serialize(job.to_dict()))
        return response
        
    if request.method == 'DELETE':
        
        resource.delete()
        
        response = HttpResponse()
        response['Content-Type'] = 'application/json'
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