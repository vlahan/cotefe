import urllib
import httplib2
import json

from models import *

SERVER_URL = 'http://localhost:8080'

class COTEFEAPI(object):
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, access_token=None):
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.http = httplib2.Http()
        
    def build_url(self, path = '/', params=dict()):
        base = path if path.startswith('http') else '%s%s' % (SERVER_URL, path)
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
    
    # creates and returns a new project
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
        