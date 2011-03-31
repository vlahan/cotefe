from django.db import models
from django.contrib.auth.models import User
from testbedserver.odict import OrderedDict
from testbedserver.config import *
from testbedserver.utils import *

class Resource(models.Model):
    class Meta:
        abstract = True

# TESTBED

class Testbed(Resource):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/"
        
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url()
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['organization'] = self.organization
            resource['users'] = resource['uri'] + 'users/'
            resource['platforms'] = resource['uri'] + 'platforms/'
            resource['jobs'] = resource['uri'] + 'jobs/'
        return resource
    
# USER

class User(Resource):
    user = models.OneToOneField(User)
    organization = models.CharField(max_length=255)
    openid = models.URLField()
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        slug = str(self.user.username)
        return "/users/%s" % slug

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.user.username
        if not head_only:
            resource['first_name'] = self.user.first_name
            resource['last_name'] = self.user.last_name
            resource['email'] = self.user.email
            resource['organization'] = self.organization
            resource['openid'] = self.openid
        return resource

# PLATFORM

class Platform(Resource):
    name = models.CharField(max_length=255)
    tinyos_name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        return "/platforms/%s" % slug
   
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['tiny_os'] = self.tinyos_name
        return resource
        
# JOB

class Job(Resource):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True)
    datetime_from = models.CharField(max_length=25)
    datetime_to = models.CharField(max_length=25)
    platforms = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
       
    def get_absolute_url(self):
        slug = str(self.id)
        return "/jobs/%s" % slug
   
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['datetime_from'] = self.datetime_from
            resource['datetime_to'] = self.datetime_to
        return resource
        
# IMAGE

class Image(Resource):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        slug = str(self.id)
        return "/images/%s" % slug

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = '/images/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        return resource
        
# NODE

class Node(Resource):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        slug = str(self.id)
        return "/nodes/%s" % slug

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = '/nodes/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        return resource
        
# NODEGROUP

class NodeGroup(Resource):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        slug = str(self.id)
        return "/nodegroups/%s" % slug

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(path = '/nodegroups/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        return resource