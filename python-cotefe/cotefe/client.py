import urllib
import requests
import utils
from models import *

class COTEFEAPI(object):
    
    def __init__(self, server_url=None, client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
    
    def _make_request(self, method, target, headers=dict(), params=None, data=None, files=None, expected_status_code=200):
        
        more_headers = dict()
        more_headers['Content-type'] = 'application/json'
        more_headers['Authorization'] = 'OAuth %s' % self.access_token
        
        headers.update(more_headers)
        
        # sometimes I want to specify the full uri, some others just the path (no server name)
        if target.startswith(self.server_url):
            url = target
        else:
            url = self.server_url + target
        
        # makes the actual request. here we are using the Requests library but any other HTTP client would do (httplib2, etc.)
        response = requests.request(method=method, url=url, headers=headers, params=params, data=data, files=files, verify=False)
        
        # makes sure that the code was as expected (default 200 OK)
        assert response.status_code == expected_status_code
        
        if expected_status_code == 201:
            
            resource_dict = self._make_request('GET', response.headers['content-location'])
            return resource_dict['id']
        
        elif expected_status_code == 202:
            
            status_dict = self._make_request('GET', response.headers['location'])
            return status_dict['id']
        
        else:
            
            return response.json
        
    # returns the url /oauth2/auth with OAuth 2.0 query parameters
    def get_authorize_url(self):
        
        params = {
          'client_id': self.client_id,
          'client_secret': self.client_secret,
          'redirect_uri': self.redirect_uri,
          'response_type': 'code'
        }
        
        return self.server_url + '/oauth2/auth?' + urllib.urlencode(params)
    
    # hits the url /oauth2/token
    def exchange_code_for_access_token(self, code):
        
        params = {
          'client_id': self.client_id,
          'client_secret': self.client_secret,
          'redirect_uri': self.redirect_uri,
          'grant_type': 'authorization_code',
          'code' : code
        }
        
        response = self._make_request('POST', '/oauth2/token', data=params, params=params)
        
        return response['access_token']
    
    # returns the current user (linked to oauth access_token
    def get_current_user(self):

        response = self._make_request('GET', '/me')
        return User(response)
    
    def get_project(self, project_id):
        
        project_dict = self._make_request('GET', '/projects/'+str(project_id))
        
        return Project(project_dict)
    
    def create_project(self, name, description):
        
        project_dict = {
            'name': name,
            'description': description,
        }
        
        project_id = self._make_request('POST', '/projects/', data=utils.serialize(project_dict), expected_status_code=201)
        
        return self.get_project(project_id)
    
    def get_experiment(self, experiment_id, project):
        
        experiment_dict = self._make_request('GET', '/experiments/'+str(experiment_id))
        
        return Experiment(experiment_dict, project)
    
    def get_platform(self, platform_id):
        
        platform_dict = self._make_request('GET', '/platforms/'+platform_id)
        
        return Platform(platform_dict)
    
    def create_experiment(self, name, description, project):
        
        experiment_dict = {
            'name': name,
            'description': description,
            'project_id': project.id
        }
        
        experiment_id = self._make_request('POST', '/experiments/', data=utils.serialize(experiment_dict), expected_status_code=201)
        
        return self.get_experiment(experiment_id, project)
    
    def get_property_set(self, peoperty_set_id, platform, experiment):
        
        property_set_dict = self._make_request('GET', '/experiments/'+str(experiment.id)+'/property-sets/'+str(peoperty_set_id))
        
        return PropertySet(property_set_dict, platform, experiment)
    
    def create_property_set(self, name, description, platform, num_nodes, experiment):
        
        property_set = {
            'name': name,
            'description': description,
            'platform_id': platform.id,
            'num_nodes': num_nodes            
        }
        
        property_set_id = self._make_request('POST', '/experiments/'+str(experiment.id)+'/property-sets/', data=utils.serialize(property_set), expected_status_code=201)
        
        return self.get_property_set(property_set_id, platform, experiment)
    
    def get_virtual_nodes(self, experiment):
        
        virtual_node_list = self._make_request('GET', '/experiments/'+str(experiment.id)+'/virtual-nodes/')
        
        virtual_nodes = list()
        
        for virtual_node_dict in virtual_node_list:
            
            virtual_nodes.append(self.get_virtual_node(virtual_node_dict['id'], experiment))
            
        return virtual_nodes
    
    def get_virtual_node(self, virtual_node_id, experiment):
        
        virtual_node_dict = self._make_request('GET', '/experiments/'+str(experiment.id)+'/virtual-nodes/'+str(virtual_node_id))
        
        return VirtualNode(virtual_node_dict, experiment)
    
    def get_virtual_nodegroup(self, virtual_nodegroup_id, experiment):
        
        virtual_nodegroup_dict = self._make_request('GET', '/experiments/'+str(experiment.id)+'/virtual-nodegroups/'+str(virtual_nodegroup_id))
        
        virtual_nodes = list()
        
        for virtual_node_dict in virtual_nodegroup_dict['virtual_nodes']:
            
            virtual_nodes.append(self.get_virtual_node(virtual_node_dict['id'], experiment))
        
        return VirtualNodeGroup(virtual_nodegroup_dict, virtual_nodes, experiment)
    
    def create_virtual_nodegroup(self, name, description, experiment, virtual_nodes):
        
        virtual_nodegroup_dict = {
            'name': name,
            'description': description,
            'expeiriment_id': experiment.id,
            'virtual_nodes': [vn.id for vn in virtual_nodes]
        }
        
        virtual_node_id = self._make_request('POST', '/experiments/'+str(experiment.id)+'/virtual-nodegroups/', data=utils.serialize(virtual_nodegroup_dict), expected_status_code=201)
        
        return self.get_virtual_nodegroup(virtual_node_id, experiment)
    
    def get_image(self, image_id, experiment):
        
        image_dict = self._make_request('GET', '/experiments/'+str(experiment.id)+'/images/'+str(image_id))
        
        return Image(image_dict, experiment)
    
    def create_image(self, name, description, imagefile, experiment):
        
        image_dict = {
            'name': name,
            'description': description,
            'experiment_id': experiment.id
        }
        
        image_id = self._make_request('POST', '/experiments/'+str(experiment.id)+'/images/', data=utils.serialize(image_dict), expected_status_code=201)
        
        image = self.get_image(image_id, experiment)
        
        self._make_request('POST', '/experiments/'+str(experiment.id)+'/images/'+str(image.id)+'/upload', files={ 'imagefile': ('imagefile', open(imagefile, 'rb')) })
                
        return self.get_image(image_id, experiment)
    
    def get_virtual_task(self, virtual_task_id, experiment):
        
        virtual_task_dict = self._make_request('GET', '/experiments/'+str(experiment.id)+'/virtual-tasks/'+str(virtual_task_id))
        
        return VirtualTask(virtual_task_dict, experiment)
    
    def create_virtual_task(self, name, description, action, virtual_nodegroup, image, experiment):
        
        if action == 'install' and image:
            
            method = 'PUT'
            target = virtual_nodegroup.uri+'/image/'+str(image.id)
            
        if action == 'erase':
            
            method = 'DELETE'
            target = virtual_nodegroup.uri+'/image'
        
        virtual_task_dict = {
            'name': name,
            'description': description,
            'experiment_id': experiment.id,
            'method': method,
            'target': target,
        }
        
        virtual_task_id = self._make_request('POST', '/experiments/'+str(experiment.id)+'/virtual-tasks/', data=utils.serialize(virtual_task_dict), expected_status_code=201)
        
        return self.get_virtual_task(virtual_task_id, experiment)