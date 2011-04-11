import logging
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from odict import OrderedDict
from utils import build_url

class Resource(polymodel.PolyModel):
    pass

class Federation(Resource):
    name = db.StringProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource = OrderedDict()
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
        
class Project(Resource):
    name = db.StringProperty()
    description = db.StringProperty()
    users = db.ListProperty(db.Key)
    testbeds = db.ListProperty(db.Key)
    experiments = db.ListProperty(db.Key)
    jobs = db.ListProperty(db.Key)
    
    def to_dict(self, head_only = False):
        resource = OrderedDict()
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
        
class User(Resource):
    user = db.UserProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        resource['uri'] = 
    
    
class Testbed(Resource):
    # STATIC INFORMATION (INSERTED BY ADMIN)
    protocol = db.StringProperty()
    host = db.StringProperty()
    port = db.StringProperty()
    
    # DYNAMIC FIELDS, RETRIEVED BY HTTP GET ON TESTBED URL
    name = db.StringProperty()
    organization = db.StringProperty()
    
    def to_dict(self, head_only = False):
        testbed = OrderedDict()
        testbed['uri'] = build_url(path = '/testbeds/' + str(self.key().id()))
        testbed['media_type'] = 'application/json'
        testbed['name'] = self.name
        if not head_only:
            testbed['organization'] = self.organization
            testbed['platforms'] = build_url(path = '/platforms/')
            testbed['jobs'] = build_url(path = '/jobs/')
        return testbed

class Platform(Resource):
    name = db.StringProperty()
    
    def to_dict(self, head_only = False):
        platform = OrderedDict()
        platform['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/' + str(self.key().id()))
        platform['media_type'] = 'application/json'
        platform['name'] = self.name            
        return platform
    
class Job(Resource):
    name = db.StringProperty()
    testbed = db.ReferenceProperty(Testbed)
    datetime_from = db.StringProperty()
    datetime_to = db.StringProperty()
    owner = db.ReferenceProperty(User)
    
    def to_dict(self, head_only = False):
        job = OrderedDict()
        job['uri'] = build_url(build_url(path = '/jobs/' + str(self.key().id()))
        job['media_type'] = 'application/json'
        job['name'] = self.name
        if not head_only:
            job['testbed'] = build_url(build_url(path = '/testbeds/' + str(self.testbed.key().id()))
            job['datetime_from'] = self.datetime_from
            job['datetime_to'] = self.datetime_to
        return job