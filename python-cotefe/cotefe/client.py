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
        
    def build_url(self, path = '/'):
        base = path if path.startswith('http') else '%s%s' % (SERVER_URL, path)
        return '%s?access_token=%s' % (base, self.access_token) if self.access_token else base
        
    # hits the url /oauth2/auth
    def get_authorize_url(self):
        
        params = {
          'client_id': self.client_id,
          'client_secret': self.client_secret,
          'redirect_uri': self.redirect_uri,
          'response_type': 'code'
        }
        
        return '%s?%s' % (self.build_url(path = '/oauth2/auth'), urllib.urlencode(params))
    
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
        response, content = self.http.request(self.build_url(path = '/oauth2/token'), method='POST', body=data)
        return json.loads(content)['access_token']
    
    def get_current_user(self):
        
        response, content = self.http.request(
            uri = self.build_url(path = '/me'),
            method='GET',
        )
        assert response.status == 200
        return User(json.loads(content))
        
    # create a new project
    def create_project(self, name, description):
        
        project_dict = {
            'name': name,
            'description': description,
        }
        response, content = self.http.request(
            uri = self.build_url(path = '/projects/'),
            method='POST',
            body = json.dumps(project_dict),
            headers = {'Content-type': 'application/json'}
        )   
        assert response.status == 201
        project_uri = response['content-location']

        response, content = self.http.request(
            uri = self.build_url(path = response['content-location']),
            method='GET',
        )
        assert response.status == 200
        return Project(json.loads(content))
        