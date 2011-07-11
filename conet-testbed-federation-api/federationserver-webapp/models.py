import logging
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from utils import build_url

class Application(db.Model):
    name = db.StringProperty()
    oauth_callback_url = db.StringProperty()
    oauth_client_id = db.StringProperty()
    oauth_client_secret = db.StringProperty()
    
class User(db.Model):
    username = db.StringProperty()
    password_hash = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.StringProperty()
    openid = db.StringProperty()
    
class OAuthSession(db.Model):
    oauth_client_id = db.StringProperty()
    oauth_response_type = db.StringProperty()
    username = db.StringProperty()
    oauth_code = db.StringProperty()
    oauth_access_token = db.StringProperty()
    oauth_refresh_token = db.StringProperty()
    oauth_scope = db.StringProperty()
    oauth_token_expire = db.StringProperty()
    
class UserResource(db.Model):
    user = db.UserProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = '/users/' + str(self.key().id()))

class FederationResource(db.Model):
    name = db.StringProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url()
        resource['media_type'] = 'application/json'
        resource['name'] = self.name
        if not head_only:
            resource['organization'] = self.organization
            resource['testbeds'] = build_url(path = '/testbeds/')
            resource['platforms'] = build_url(path = '/platforms/')
            resource['users'] = build_url(path = '/users/')
            resource['jobs'] = build_url(path = '/jobs/')
        return resource
        
class ProjectResource(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    users = db.ListProperty(db.Key)
    testbeds = db.ListProperty(db.Key)
    experiments = db.ListProperty(db.Key)
    jobs = db.ListProperty(db.Key)
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = '/projects/' + str(self.key().id()))
        resource['media_type'] = 'application/json'
        resource['name'] = self.name
        if not head_only:
            resource['description'] = self.description
            resource['users'] = build_url(path = '/users/')
            resource['testbeds'] = build_url(path = '/testbeds/')
            resource['experiments'] = build_url(path = '/experiments/')
            resource['jobs'] = build_url(path = '/jobs/')
        return resource

class ExperimentResource(db.Model):
    name = db.StringProperty()
    description = db.StringProperty()
    
    
class TestbedResource(db.Model):
    # STATIC INFORMATION (INSERTED BY ADMIN)
    protocol = db.StringProperty()
    host = db.StringProperty()
    port = db.StringProperty()
    
    # DYNAMIC FIELDS, RETRIEVED BY HTTP GET ON TESTBED URL
    name = db.StringProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = '/testbeds/' + str(self.key().id()))
        resource['media_type'] = 'application/json'
        resource['name'] = self.name
        if not head_only:
            resource['organization'] = self.organization
            resource['platforms'] = build_url(path = '/platforms/')
            resource['jobs'] = build_url(path = '/jobs/')
        return resource

class PlatformResource(db.Model):
    name = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = '/platforms/' + str(self.key().id()))
        resource['media_type'] = 'application/json'
        resource['name'] = self.name            
        return resource
    
class JobResource(db.Model):
    name = db.StringProperty()
    testbed = db.ReferenceProperty(TestbedResource)
    datetime_from = db.StringProperty()
    datetime_to = db.StringProperty()
    owner = db.ReferenceProperty(UserResource)
    
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = '/jobs/' + str(self.key().id()))
        resource['media_type'] = 'application/json'
        resource['name'] = self.name
        if not head_only:
            resource['testbed'] = build_url(path = '/testbeds/' + str(self.testbed.key().id()))
            resource['datetime_from'] = self.datetime_from
            resource['datetime_to'] = self.datetime_to
        return resource