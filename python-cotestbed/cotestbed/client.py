import sys
import urllib
import requests
import utils
from models import *

class COTESTBEDAPI(object):
    
    def __init__(self, server_url=None, client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        
        self.server_url = server_url
    
    def _make_request(self, method, target, headers=dict(), params=None, data=None, files=None, expected_status_code=200):
        
        more_headers = dict()
        # more_headers['Content-type'] = 'application/json'
        
        headers.update(more_headers)
        
        # sometimes I want to specify the full uri, some others just the path (no server name)
        if target.startswith(self.server_url):
            url = target
        else:
            url = self.server_url + target
        
        # makes the actual request. here we are using the Requests library but any other HTTP client would do (httplib2, etc.)
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            files=files,
            verify=False,
            # config={'verbose': sys.stdout}
        )
        
        # makes sure that the code was as expected (default 200 OK)
        assert response.status_code == expected_status_code
        
        if expected_status_code == 201:
            
            resource_dict = self._make_request('GET', response.headers['content-location'])
            return resource_dict['id']
        
        else:
            
            return response.json
    
    def get_testbed(self):
        
        testbed_dict = self._make_request('GET', '/')
        
        return Testbed(testbed_dict)
        
    def get_nodes(self, n=None, platform=None):
        
        params = dict()
        
        if n: params['n'] = n
        if platform: params['platform'] = platform
        
        node_list = self._make_request('GET', '/nodes/', params=params)
        
        nodes = list()
        
        for node_dict in node_list:
            
            nodes.append(self.get_node(node_dict['id']))
            
        return nodes
    
    def get_node(self, node_id):
        
        node_dict = self._make_request('GET', '/nodes/'+node_id)
        
        return Node(node_dict)
    
    def get_jobs(self, date_from=None, date_to=None):
        
        params = dict()
        
        if date_from: params['date_from'] = date_from
        if date_to: params['date_to'] = date_to
        
        job_list = self._make_request('GET', '/jobs/', params=params)
        
        jobs = list()
        
        for job_dict in job_list:
            
            jobs.append(self.get_job(job_dict['id']))
            
        return jobs
    
    def get_job(self, job_id):
        
        job_dict = self._make_request('GET', '/jobs/'+job_id)
        
        node_list = list()
        
        for node_dict in job_dict['nodes']:
            
            node_list.append(self.get_node(node_dict['id']))
        
        return Job(job_dict, node_list)
    
    def create_job(self, name, description, datetime_from, datetime_to, nodes):
        
        job_dict = {
            'name': name,
            'description': description,
            'datetime_from': utils.datetime_to_string(datetime_from),
            'datetime_to': utils.datetime_to_string(datetime_to),
            'nodes': [node.id for node in nodes]
        }
        
        job_id = self._make_request('POST', '/jobs/', data=utils.serialize(job_dict), expected_status_code=201)
        
        return self.get_job(job_id)
    
    def get_nodegroup(self, nodegroup_id, job):
        
        nodegroup_dict = self._make_request('GET', '/nodegroups/'+nodegroup_id)
        
        nodes = list()
        
        for node_dict in nodegroup_dict['nodes']:
            
            nodes.append(self.get_node(node_dict['id']))
        
        return NodeGroup(nodegroup_dict, job, nodes)
    
    def create_nodegroup(self, name, description, job, nodes):
        
        nodegroup_dict = {
            'name': name,
            'description': description,
            'job': job.id,
            'nodes': [node.id for node in nodes]
        }
        
        nodegroup_id = self._make_request('POST', '/nodegroups/', data=utils.serialize(nodegroup_dict), expected_status_code=201)
        
        return self.get_nodegroup(nodegroup_id, job)
    
    def get_image(self, image_id, job):
        
        image_dict = self._make_request('GET', '/images/'+image_id)
        
        return Image(image_dict, job)
    
    def create_image(self, name, description, imagefile, job):
        
        image_dict = {
            'name': name,
            'description': description,
            'job': job.id,
        }
        
        image_id = self._make_request('POST', '/images/', data=utils.serialize(image_dict), expected_status_code=201)
        
        image = self.get_image(image_id, job)
        
        self._make_request('POST', '/images/'+image.id+'/upload', files={'imagefile': open(imagefile, 'rb')})
        
        return self.get_image(image_id, job)
        
#    def create_virtual_task(self, name, description, action, virtual_nodegroup, image, experiment):
#        
#        method = {
#            'install': 'PUT',
#            'erase': 'DELETE'
#        }
#        
#        vt_dict = {
#            'name': name,
#            'description': description,
#            'method': method[action]
#        }
#        
#        if image:
#            vt_dict['target'] = self.build_uri(path = '%s/image/%s' % (virtual_nodegroup.uri, image.id))
#        else:
#            vt_dict['target'] = self.build_uri(path = '%s/image' % virtual_nodegroup.uri)
#        
#        uri = self.build_uri(path = '/experiments/%s/virtual-tasks/' % experiment.id)
#        method = 'POST'
#        headers = self.build_headers()
#        body = utils.serialize(vt_dict)
#        response, content = self.http.request(uri=uri, method=method, headers=headers, body=body)
#        assert response.status == 201
#
#        uri = self.build_uri(path = response['content-location'])
#        method = 'GET'
#        headers = self.build_headers()
#        response, content = self.http.request(uri=uri, method=method, headers=headers)
#        assert response.status == 200
#        
#        return VirtualTask(utils.deserialize(content), experiment)
        