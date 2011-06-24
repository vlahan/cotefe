from django.db import models
from django.contrib.auth.models import User
from testbedserver.config import *
from testbedserver.utils import *

# RESOURCE ABSTRACT MODEL
class Resource(models.Model):
    class Meta:
        abstract = True
        
# USER
#class User(Resource):
#    user = models.OneToOneField(User)
#    organization = models.CharField(max_length=255)
#    openid = models.URLField()
#
#    def __unicode__(self):
#        return self.user.username
#
#    def get_absolute_url(self):
#        slug = str(self.user.username)
#        return "/users/%s" % slug
#
#    def to_dict(self, head_only = False):
#        resource = dict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        if not head_only:
#            resource['name'] = self.user.username
#            resource['first_name'] = self.user.first_name
#            resource['last_name'] = self.user.last_name
#            resource['email'] = self.user.email
#            resource['organization'] = self.organization
#            resource['openid'] = self.openid
#        return resource
#
#    class Meta:
#        verbose_name = "User"
#        verbose_name_plural = verbose_name +'s'
        
# TESTBED
class Testbed(Resource):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/"
        
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url()
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['organization'] = self.organization
            resource['description'] = self.description
            resource['platforms'] = build_url(path = '/platforms/')
            resource['nodes'] = build_url(path = '/nodes/')
            resource['jobs'] = build_url(path = '/jobs/')
        return resource
        
    class Meta:
        verbose_name = "Testbed"
        verbose_name_plural = verbose_name +'s'

# JOB
class Platform(Resource):
    uid = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    tinyos_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.uid

    def get_absolute_url(self):
        return "/platforms/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            # resource['native_id'] = self.native_id
            resource['tinyos_name'] = self.tinyos_name
        return resource

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = verbose_name +'s'
        
# IMAGE
class Image(Resource):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='images')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        slug = str(self.id)
        return "/images/%s" % slug

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['file'] = self.file
        return resource

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'

# JOB
#class Job(Resource):
#    uid = models.CharField(max_length=255, unique=True)
#    name = models.CharField(max_length=255)
#    datetime_from = models.CharField(max_length=25)
#    datetime_to = models.CharField(max_length=25)
#
#    def __unicode__(self):
#        return self.uid
#
#    def get_absolute_url(self):
#        return "/jobs/%s" % self.uid
#
#    def to_dict(self, head_only = False):
#        resource = dict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        if not head_only:
#            resource['name'] = self.name
#            resource['datetime_from'] = self.datetime_from
#            resource['datetime_to'] = self.datetime_to
#        return resource
#
#    class Meta:
#        verbose_name = "Job"
#        verbose_name_plural = verbose_name +'s'
    
# NODE
class Node(Resource):
    uid = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    serial = models.CharField(max_length=255, unique=True)
    # platform = models.ForeignKey(Platform)
    
    def __unicode__(self):
        return self.uid

    def get_absolute_url(self):
        return "/nodes/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            # resource['native_id'] = self.native_id
            resource['serial'] = self.serial
        return resource
    
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = verbose_name +'s'
        
# NODEGROUP
class NodeGroup(Resource):
    name = models.CharField(max_length=255)
    description = models.TextField()
    nodes = models.TextField()
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        slug = str(self.id)
        return "/nodegroups/%s" % slug

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
        return resource
        
    class Meta:
        verbose_name = "NodeGroup"
        verbose_name_plural = verbose_name +'s'
        
# TASK
#class Task(Resource):
#    name = models.CharField(max_length=255)
#    description = models.TextField()
#
#    def __unicode__(self):
#        return self.name
#
#    def get_absolute_url(self):
#        slug = str(self.id)
#        return "/tasks/%s" % slug
#
#    def to_dict(self, head_only = False):
#        resource = dict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        if not head_only:
#            resource['name'] = self.name
#            resource['description'] = self.description
#        return resource
#
#    class Meta:
#        verbose_name = "Task"
#        verbose_name_plural = verbose_name +'s'
                
# TRACE
#class Trace(Resource):
#    name = models.CharField(max_length=255)
#    description = models.TextField()
#
#    def __unicode__(self):
#        return self.name
#
#    def get_absolute_url(self):
#        slug = str(self.id)
#        return "/traces/%s" % slug
#
#    def to_dict(self, head_only = False):
#        resource = dict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        if not head_only:
#            resource['name'] = self.name
#            resource['description'] = self.description
#        return resource
#
#    class Meta:
#        verbose_name = "Trace"
#        verbose_name_plural = verbose_name +'s'
        
# LOG
#class Log(Resource):
#    name = models.CharField(max_length=255)
#    description = models.TextField()
#
#    def __unicode__(self):
#        return self.name
#
#    def get_absolute_url(self):
#        slug = str(self.id)
#        return "/logs/%s" % slug
#
#    def to_dict(self, head_only = False):
#        resource = dict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        if not head_only:
#            resource['name'] = self.name
#            resource['description'] = self.description
#        return resource
#
#    class Meta:
#        verbose_name = "Log"
#        verbose_name_plural = verbose_name +'s'

