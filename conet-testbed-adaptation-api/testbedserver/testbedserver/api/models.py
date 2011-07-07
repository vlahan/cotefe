import os
from django.db import models
from django.contrib.auth.models import User
from testbedserver.settings import *
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
#        resource = OrderedDict()
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
        resource['name'] = self.name
        if not head_only:
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
        verbose_name_plural = verbose_name

# JOB
class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    tinyos_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/platforms/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['tinyos_name'] = self.tinyos_name
            # resource['native_id'] = self.native_id
        return resource

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = verbose_name +'s'

# returns random filename
def update_filename(instance, filename):
    filepath = 'images'
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.id, ext)
    return os.path.join(filepath, filename)
        
# IMAGE
class Image(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to=update_filename)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/images/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
            resource['file'] = build_url(path = '/static/' + self.file.name)
        return resource

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'

# JOB
class Job(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/jobs/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
            resource['datetime_from'] = utc_datetime_to_utc_string(self.datetime_from)
            resource['datetime_to'] = utc_datetime_to_utc_string(self.datetime_to)
            resource['nodes'] = build_url(path = self.get_absolute_url() + '/nodes/')
        return resource

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = verbose_name +'s'
    
# NODE
class Node(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, unique=True)
    platform = models.ForeignKey(Platform)
    image = models.ForeignKey(Image, null=True, blank=True)
    
    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/nodes/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['platform'] = build_url(path = self.platform.get_absolute_url())
            if self.image:
                resource['image'] = build_url(path = self.image.get_absolute_url())
            else:
                resource['image'] = None
        return resource
    
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = verbose_name +'s'
        
# NODEGROUP
class NodeGroup(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ForeignKey(Image, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/nodegroups/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
            resource['nodes'] = build_url(path = self.get_absolute_url() + '/nodes/')
            if self.image:
                resource['image'] = build_url(path = self.image.get_absolute_url())
            else:
                resource['image'] = None
        return resource
        
    class Meta:
        verbose_name = "NodeGroup"
        verbose_name_plural = verbose_name +'s'

class NodeGroup2Node(models.Model):
    nodegroup = models.ForeignKey(NodeGroup, verbose_name='NodeGroup', related_name='nodes')
    node = models.ForeignKey(Node, verbose_name='Node', related_name='nodegroups')
    
    def __unicode__(self):
        return u'%s %s' % (self.nodegroup, self.node)
    
    class Meta:
        verbose_name = "NodeGroup2Node"
        verbose_name_plural = verbose_name +'s'

class Job2Node(models.Model):
    job = models.ForeignKey(Job, verbose_name='Job', related_name='nodes')
    node = models.ForeignKey(Node, verbose_name='Node', related_name='jobs')
    
    def __unicode__(self):
        return u'%s %s' % (self.job, self.node)
    
    class Meta:
        verbose_name = "Job2Node"
        verbose_name_plural = verbose_name +'s'
        

