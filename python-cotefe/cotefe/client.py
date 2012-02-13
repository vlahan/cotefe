import urllib
import httplib2
import json
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from models import *

class COTEFEAPI(object):
    
    def __init__(self, server_url='https://api.cotefe.net', client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
        
    def build_url(self, path = '/', params=dict()):
        base = path if path.startswith('http') else '%s%s' % (self.server_url, path)
        if self.access_token:
            params.update(access_token = self.access_token)
        return '%s?%s' % (base, urllib.urlencode(params))
        
    # hits the url /oauth2/auth
    def get_authorize_url(self):
        
        params = {
          'client_id': self.client_id,
          'client_secret': self.client_secret,
          'redirect_uri': self.redirect_uri,
          'response_type': 'code'
        }
        
        return self.build_url('/oauth2/auth', params)
    
    # hits the url /oauth2/token
    def exchange_code_for_access_token(self, code):
        
        params = {
          'client_id': self.client_id,
          'client_secret': self.client_secret,
          'redirect_uri': self.redirect_uri,
          'grant_type': 'authorization_code',
          'code' : code
        }
        
        data = urllib.urlencode(params)
        response, content = self.http.request(self.build_url('/oauth2/token'), method='POST', body=data)
        return json.loads(content)['access_token']
    
    # returns the current user (linked to oauth access_token
    def get_current_user(self):
        
        response, content = self.http.request(
            uri = self.build_url(path = '/me'),
            method='GET',
        )
        assert response.status == 200
        return User(json.loads(content))
        
    # creates and returns a new project
    def create_project(self, name, description):
        
        project_dict = {
            'name': name,
            'description': description,
        }
        
        uri = self.build_url(path = '/projects/')
        method = 'POST'
        headers = {'Content-type': 'application/json'}
        body = json.dumps(project_dict)
        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
        assert response.status == 201
        
        uri = self.build_url(path = response['content-location'])
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        return Project(json.loads(content))
    
    # creates and returns a new experiment
    def create_experiment(self, name, description, project):
        
        experiment_dict = {
            'name': name,
            'description': description,
            'project_id': project.id
        }
        
        uri = self.build_url(path = '/experiments/')
        method = 'POST'
        headers = {'Content-type': 'application/json'}
        body = json.dumps(experiment_dict)
        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
        assert response.status == 201

        uri = self.build_url(path = response['content-location'])
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        return Experiment(json.loads(content), project)
    
    # returns a list of platforms matching the specified name
    def search_platform(self, name):
        
        uri = self.build_url(path = '/platforms/', params = { 'name': name })
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        platform_list = json.loads(content)
        
        platforms = list()
        
        for platform_dict in platform_list:
            
            uri = self.build_url(path = platform_dict['uri'])
            method = 'GET'
            response, content = self.http.request(uri=uri, method=method)
            assert response.status == 200
            
            platform_dict = json.loads(content)
            
            platforms.append(Platform(platform_dict))
            
        return platforms
    
    # creates and returns a new property set
    def create_property_set(self, name, description, platform, num_nodes, experiment):
        
        property_set_dict = {
            'name': name,
            'description': description,
            'platform_id': platform.id,
            'num_nodes': num_nodes
        }
        
        uri = self.build_url(path = '/experiments/%s/property-sets/' % experiment.id)
        method = 'POST'
        headers = {'Content-type': 'application/json'}
        body = json.dumps(property_set_dict)
        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
        assert response.status == 201

        uri = self.build_url(path = response['content-location'])
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        return PropertySet(json.loads(content), platform, experiment)
        
    # getting the virtual nodes for a given experiment
    def get_virtual_nodes(self, experiment):
        
        uri = self.build_url(path = '/experiments/%s/virtual-nodes/' % experiment.id)
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        virtual_node_list = json.loads(content)
        
        virtual_nodes = list()
        
        for virtual_node_dict in virtual_node_list:
            
            uri = self.build_url(path = virtual_node_dict['uri'])
            method = 'GET'
            response, content = self.http.request(uri=uri, method=method)
            assert response.status == 200
            
            virtual_node_dict = json.loads(content)
            
            virtual_nodes.append(VirtualNode(virtual_node_dict, experiment))
            
        return virtual_nodes
        
    def create_virtual_nodegroup(self, name, description, virtual_nodes, experiment):
        
        vng_dict = {
            'name': name,
            'description': description,
            'virtual_nodes': [ vn.id for vn in virtual_nodes ]
        }
        
        uri = self.build_url(path = '/experiments/%s/virtual-nodegroups/' % experiment.id)
        method = 'POST'
        headers = {'Content-type': 'application/json'}
        body = json.dumps(vng_dict)
        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
        assert response.status == 201

        uri = self.build_url(path = response['content-location'])
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        return VirtualNodeGroup(json.loads(content), virtual_nodes, experiment)
        
    def create_image(self, name, description, imagefile, experiment):
        
        image_dict = {
            'name': name,
            'description': description,
        }
        
        uri = self.build_url(path = '/experiments/%s/images/' % experiment.id)
        method = 'POST'
        headers = {'Content-type': 'application/json'}
        body = json.dumps(image_dict)
        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
        assert response.status == 201

        uri = self.build_url(path = response['content-location'])
        method = 'GET'
        response, content = self.http.request(uri=uri, method=method)
        assert response.status == 200
        
        image_dict = json.loads(content)
        
        register_openers()
        datagen, headers = multipart_encode({'imagefile': open(imagefile, 'rb')})
        request = urllib2.Request(self.build_url(path = image_dict['upload']), datagen, headers)
        urllib2.urlopen(request).read()
        
        return Image(image_dict, experiment)