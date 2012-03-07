import logging
from collections import OrderedDict

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

import config
from utils import build_url, convert_datetime_to_string

# class Resource(polymodel.PolyModel):
class Resource(db.Model):
    pass

class Relationship(db.Model):
    pass

class User(Resource):
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
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/users/%s' % self.id())
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['username'] = self.username
        r['id'] = self.id()
        if not head_only:
            r['first'] = self.first
            r['last'] = self.last
            r['email'] = self.email
            r['organization'] = self.organization
            r['projects'] = [ p.to_dict(head_only = True) for p in self.projects ]
            r['experiments'] = [ e.to_dict(head_only = True) for e in self.experiments ]
            r['jobs'] = [ j.to_dict(head_only = True) for j in self.jobs ]
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
    

class Federation(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def to_dict(self):
        r = OrderedDict()
        r['uri'] = build_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['description'] = self.description
        r['testbeds'] = build_url(path = '/testbeds/')
        r['platforms'] = build_url(path = '/platforms/')
        r['projects'] = build_url(path = '/projects/')
        r['experiments'] = build_url(path = '/experiments/')
        # r['jobs'] = build_url(path = '/jobs/')
        r['users'] = build_url(path = '/users/')
        r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
        r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class Testbed(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    organization = db.StringProperty()
    homepage = db.LinkProperty()
    server_url = db.LinkProperty()
    node_count = db.IntegerProperty()
    
    background_image_url = db.LinkProperty()
    coordinates_mapping_function_x = db.StringProperty()
    coordinates_mapping_function_y = db.StringProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/testbeds/%s' % self.id())
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['organization'] = self.organization
            r['server_url'] = self.server_url
            r['platforms'] = build_url(path = '/platforms/')
            r['nodes'] = build_url(path = '/nodes/')
            r['node_count'] = self.node_count
            r['jobs'] = build_url(path = '/jobs/')
            
            r['background_image_url'] = self.background_image_url
            r['coordinates_mapping_function_x'] = self.coordinates_mapping_function_x
            r['coordinates_mapping_function_y'] = self.coordinates_mapping_function_y
            
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
class Platform(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/platforms/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
class Interface(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/interfaces/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class Sensor(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/sensors/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
class Actuator(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/actuators/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class Project(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    owner = db.ReferenceProperty(User, collection_name='projects')

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/projects/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['owner'] = self.owner.to_dict(head_only = True)
            r['experiments'] = [ e.to_dict(head_only = True) for e in self.experiments ]
            r['experiment_count'] = len(r['experiments'])
            # r['members'] = [ User.get_by_id(user_key.id()).to_dict(head_only = True) for user_key in self.members ]
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
#class ProjectMembership(Relationship):
#    member = db.ReferenceProperty(User, collection_name='projects')
#    project = db.ReferenceProperty(Project, collection_name='members')
        
class Experiment(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    owner = db.ReferenceProperty(User, collection_name='experiments')
    project = db.ReferenceProperty(Project, collection_name='experiments')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/experiments/%s' % self.id())

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            try:
                r['owner'] = self.owner.to_dict(head_only = True)
            except:
                r['owner'] = None
            try:
                r['project'] = self.project.to_dict(head_only = True)
            except:
                r['project'] = None
            r['images'] = [ i.to_dict(head_only = True) for i in self.images ]
            r['property_sets'] = [ ps.to_dict(head_only = True) for ps in self.property_sets ]
            r['virtual_nodes'] = [ vn.to_dict(head_only = True) for vn in self.virtual_nodes ]
            r['virtual_node_count'] = len(r['virtual_nodes'])
            r['virtual_node_groups'] = [ vng.to_dict(head_only = True) for vng in self.virtual_node_groups ]
            r['virtual_tasks'] = [ vt.to_dict(head_only = True) for vt in self.virtual_tasks ]
            r['jobs'] = [ j.to_dict(head_only = True) for j in self.jobs ]
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
    
    
class Image(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    imagefile = db.BlobProperty()
    
    owner = db.ReferenceProperty(User, collection_name='images')
    experiment = db.ReferenceProperty(Experiment, collection_name='images')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
    
    def uri(self):
        return build_url(path = '/experiments/%s/images/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            if self.imagefile:
                r['download'] = '%s/download' % self.uri()
            r['upload'] = '%s/upload' % self.uri()
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
            

class PropertySet(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    owner = db.ReferenceProperty(User, collection_name='property_sets')
    platform = db.ReferenceProperty(Platform)
    # sensors = db.ListProperty(db.Key)
    # actuators = db.ListProperty(db.Key)
    num_nodes = db.IntegerProperty()
    
    experiment = db.ReferenceProperty(Experiment, collection_name='property_sets')

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return self.key().id()
    
    def uri(self):
        return build_url(path = '/experiments/%s/property-sets/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            try:
                r['project'] = self.project.to_dict(head_only = True)
            except:
                r['project'] = None
            r['platform'] = self.platform.to_dict(head_only = True)
            r['num_nodes'] = self.num_nodes
            r['virtual_nodes'] = [ vn.to_dict(head_only = True) for vn in self.virtual_nodes ]
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
            
class VirtualNode(Resource):
    name = db.StringProperty()
    
    owner = db.ReferenceProperty(User, collection_name='virtual_nodes')
    platform = db.ReferenceProperty(Platform, collection_name='virtual_nodes')
    experiment = db.ReferenceProperty(Experiment, collection_name='virtual_nodes')
    property_set = db.ReferenceProperty(PropertySet, collection_name='virtual_nodes')
    image = db.ReferenceProperty(Image, collection_name='virtual_nodes')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
    
    def uri(self):
        return build_url(path = '/experiments/%s/virtual-nodes/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['platform'] = self.platform.to_dict(head_only = True)
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            try:
                r['project'] = self.experiment.project.to_dict(head_only = True)
            except:
                r['project'] = None
            try:
                r['property_set'] = self.property_set.to_dict(head_only = True)
            except:
                r['property_set'] = None
            r['virtual_nodegroups'] = [ vng2vn.vng.to_dict(head_only = True) for vng2vn in self.virtual_nodegroups ]
            try:
                r['image'] = self.image.to_dict(head_only = True)
            except:
                r['image'] = None
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
            
class VirtualNodeGroup(Resource):
    name = db.StringProperty()
    description = db.TextProperty()

    experiment = db.ReferenceProperty(Experiment, collection_name='virtual_node_groups')
    image = db.ReferenceProperty(Image, collection_name='virtual_node_groups')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()

    def uri(self):
        return build_url(path = '/experiments/%s/virtual-nodegroups/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            try:
                r['project'] = self.experiment.project.to_dict(head_only = True)
            except:
                r['project'] = None
            r['virtual_nodes'] = [ vng2vn.vn.to_dict(head_only = True) for vng2vn in self.virtual_nodes ]
            r['virtual_node_count'] = len(r['virtual_nodes'])
            try:
                r['image'] = self.image.uri()
            except:
                r['image'] = None
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
        
class VirtualNodeGroup2VirtualNode(Relationship):
   vng = db.ReferenceProperty(VirtualNodeGroup, collection_name='virtual_nodes')
   vn = db.ReferenceProperty(VirtualNode, collection_name='virtual_nodegroups')
            
class VirtualTask(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    order = db.IntegerProperty()
    
    method = db.StringProperty()
    target = db.LinkProperty()
    
    experiment = db.ReferenceProperty(Experiment, collection_name='virtual_tasks')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()

    def uri(self):
        return build_url(path = '/experiments/%s/virtual-tasks/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['method'] = self.method
            r['target'] = self.target
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            try:
                r['project'] = self.experiment.project.to_dict(head_only = True)
            except:
                r['project'] = None            
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r
            
class Job(Resource):
    name = db.StringProperty()
    description = db.TextProperty()
    
    datetime_from = db.DateTimeProperty()
    datetime_to = db.DateTimeProperty()
    
    owner = db.ReferenceProperty(User, collection_name='jobs')
    testbed = db.ReferenceProperty(Testbed)
    experiment = db.ReferenceProperty(Experiment, collection_name='jobs')
    
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()

    def uri(self):
        return build_url(path = '/jobs/%s' % (self.experiment.id(), self.id()))

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id()
        if not head_only:
            r['description'] = self.description
            r['datetime_from'] = convert_datetime_to_string(self.datetime_from)
            r['datetime_to'] = convert_datetime_to_string(self.datetime_to)
            r['testbed'] = self.testbed.to_dict(head_only = True)
            
            try:
                r['experiment'] = self.experiment.to_dict(head_only = True)
            except:
                r['experiment'] = None
            try:
                r['project'] = self.experiment.project.to_dict(head_only = True)
            except:
                r['project'] = None
            try:
                r['property_set'] = self.property_set.to_dict(head_only = True)
            except:
                r['property_set'] = None
            
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class Task(Resource):
    name = db.StringProperty()
    description = db.TextProperty()

    target = db.LinkProperty()
    
    virtual_task = db.ReferenceProperty(VirtualTask)
    job = db.ReferenceProperty(Job)

    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)

    def id(self):
        return self.key().id()

    def uri(self):
        return build_url(path = '/tasks/%s' % self.id())

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
        return r