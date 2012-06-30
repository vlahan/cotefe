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
        

        