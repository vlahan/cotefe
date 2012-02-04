import logging
from collections import OrderedDict

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

import config
from utils import build_url, convert_datetime_to_string

class User(db.Model):
    username = db.StringProperty()
    # password = db.StringProperty()
    first = db.StringProperty()
    last = db.StringProperty()
    email = db.StringProperty()
    organization = db.StringProperty()
    admin = db.BooleanProperty()
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())
        
    def uri(self):
        return build_url(path = '/users/' + self.id())
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.username
        if not head_only:
            r['first'] = self.first
            r['last'] = self.last
            r['email'] = self.email
            r['organization'] = self.organization
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
class OpenIDIdentity(db.Model):
    identifier = db.StringProperty()
    provider = db.StringProperty()
    user = db.ReferenceProperty(User)
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

class Application(db.Model):
    name = db.StringProperty()
    client_id = db.StringProperty()
    client_secret = db.StringProperty()
    redirect_uri = db.LinkProperty()
    owner = db.ReferenceProperty(User)
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

class OAuth2Session(db.Model):
    application = db.ReferenceProperty(Application)
    user = db.ReferenceProperty(User)
    code = db.StringProperty()
    access_token = db.StringProperty()
    refresh_token = db.StringProperty()
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    
class Resource(polymodel.PolyModel):
    pass

class Federation(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['testbeds'] = build_url(path = '/testbeds/')
            r['platforms'] = build_url(path = '/platforms/')
            r['projects'] = build_url(path = '/projects/')
            r['experiments'] = build_url(path = '/experiments/')
            r['jobs'] = build_url(path = '/jobs/')
            r['users'] = build_url(path = '/users/')
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class Testbed(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    organization = db.StringProperty()
    server_url = db.LinkProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())
        
    def uri(self):
        return build_url(path = '/testbeds/' + self.id())
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['organization'] = self.organization
            r['server_url'] = self.server_url
            r['platforms'] = build_url(path = '/platforms/')
            r['nodes'] = build_url(path = '/nodes/')
            r['jobs'] = build_url(path = '/jobs/')
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class Project(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    owner = db.ReferenceProperty(User)
    members = db.ListProperty(db.Key)

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return str(self.key().id())
        
    def uri(self):
        return build_url(path = '/projects/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['owner'] = self.owner.to_dict(head_only = True)
            r['members'] = [ User.get_by_id(user_key.id()).to_dict(head_only = True) for user_key in self.members ]
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class Experiment(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    project = db.ReferenceProperty(Project)
    owner = db.ReferenceProperty(User)

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return str(self.key().id())
        
    def uri(self):
        return build_url(path = '/experiments/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class Platform(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())
        
    def uri(self):
        return build_url(path = '/platforms/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class PropertySet(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    platform = db.ReferenceProperty(Platform)
    # sensors = db.ListProperty(db.Key)
    # actuators = db.ListProperty(db.Key)
    virtual_node_count = db.IntegerProperty()
    
    experiment = db.ReferenceProperty(Experiment)

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return str(self.key().id())
    
    def uri(self):
        return build_url(path = '/property-sets/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['experiment'] = self.experiment.uri()
            r['virtual_node_count'] = self.virtual_node_count
            r['platform'] = self.platform.uri()
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class Image(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    image_url = db.LinkProperty()
    
    experiment = db.ReferenceProperty(Experiment)
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())
    
    def uri(self):
        return build_url(path = '/images/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['image_url'] = self.image_url
            r['experiment'] = self.experiment.uri()
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
            
class VirtualNode(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    platform = db.ReferenceProperty(Platform)
    experiment = db.ReferenceProperty(Experiment)
    property_set = db.ReferenceProperty(PropertySet)
    image = db.ReferenceProperty(Image)
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())
    
    def uri(self):
        return build_url(path = '/virtual-nodes/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['platform'] = self.platform.uri()
            r['experiment'] = self.experiment.uri()
            r['property_set'] = self.property_set.uri()
            r['image'] = self.image.uri() if self.image else None
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
            
class VirtualNodeGroup(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    virtual_nodes = db.ListProperty(db.Key)
    
    virtual_node_count = db.IntegerProperty()

    experiment = db.ReferenceProperty(Experiment)
    image = db.ReferenceProperty(Image)
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())

    def uri(self):
        return build_url(path = '/virtual-nodegroups/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['virtual_nodes'] = [ VirtualNode.get(key).to_dict(head_only = True) for key in self.virtual_nodes]
            r['virtual_node_count'] = self.virtual_node_count
            r['experiment'] = self.experiment.uri()
            r['image'] = self.image.uri() if self.image else None
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
            
class VirtualTask(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    method = db.StringProperty()
    target = db.LinkProperty()
    
    experiment = db.ReferenceProperty(Experiment)
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())

    def uri(self):
        return build_url(path = '/virtual-tasks/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['method'] = self.method
            r['target'] = self.target
            
            r['experiment'] = self.experiment.uri()
            
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
            
class Job(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_from = db.DateTimeProperty()
    datetime_to = db.DateTimeProperty()
    
    testbed = db.ReferenceProperty(Testbed)
    experiment = db.ReferenceProperty(Experiment)
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return str(self.key().id())

    def uri(self):
        return build_url(path = '/jobs/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['datetime_from'] = convert_datetime_to_string(self.datetime_from)
            r['datetime_to'] = convert_datetime_to_string(self.datetime_to)
            
            r['testbed'] = self.testbed.uri()
            r['experiment'] = self.experiment.uri()
            
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)

class Task(Resource):
    name = db.StringProperty()
    description = db.TextProperty()

    target = db.LinkProperty()
    
    virtual_task = db.ReferenceProperty(VirtualTask)
    job = db.ReferenceProperty(Job)

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return str(self.key().id())

    def uri(self):
        return build_url(path = '/tasks/' + self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['method'] = self.method
            r['target'] = self.target

            r['virtual_task'] = self.virtual_task.uri()
            r['job'] = self.job.uri()

            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)