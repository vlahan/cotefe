import os
from django.db import models
from django.contrib.auth.models import User
from testbedserver.config import *
from testbedserver.utils import *
from testbedserver.settings import PROJECT_PATH

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
            resource['nodegroups'] = build_url(path = '/nodegroups/')
            resource['jobs'] = build_url(path = '/jobs/')
            resource['images'] = build_url(path = '/images/')
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

# returns random filename
def update_filename(instance, filename):
    filepath = 'images'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.uid, ext)
    return os.path.join(filepath, filename)
        
# IMAGE
class Image(Resource):
    uid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to=update_filename, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/images/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['file'] = build_url(path = '/static/' + self.file.name)
        return resource

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'

# JOB
class Job(Resource):
    uid = models.CharField(max_length=255, unique=True)
    native_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()

    def __unicode__(self):
        return self.uid

    def get_absolute_url(self):
        return "/jobs/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['datetime_from'] = self.datetime_from
            resource['datetime_to'] = self.datetime_to
        return resource

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = verbose_name +'s'
    
# NODE
class Node(Resource):
    uid = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    serial = models.CharField(max_length=255, unique=True)
    platform = models.ForeignKey(Platform)
    
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
            resource['platform'] = build_url(path = self.platform.get_absolute_url())
        return resource
    
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = verbose_name +'s'
        
# NODEGROUP
class NodeGroup(Resource):
    uid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/nodegroups/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['nodes'] = build_url(path = self.get_absolute_url() + '/nodes/')
        return resource
        
    class Meta:
        verbose_name = "NodeGroup"
        verbose_name_plural = verbose_name +'s'

class NodeGroup2Node(models.Model):
    nodegroup = models.ForeignKey(NodeGroup, verbose_name='NodeGroup')
    node = models.ForeignKey(Node, verbose_name='Node')
    
    def __unicode__(self):
        return u'%s %s' % (self.nodegroup, self.node)
    
    class Meta:
        verbose_name = "NodeGroup2Node"
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

