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
        verbose_name_plural = verbose_name + 's'

class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/platforms/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(server_url = FEDERATION_URL, path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
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
    file = models.FileField(upload_to=update_filename, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/images/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            if self.file:
                resource['file'] = build_url(path = '/static/' + self.file.name)
            else:
                resource['file'] = None
            resource['imagefile_upload'] = build_url(path = '%s/upload' % self.get_absolute_url())
        return resource

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'


# JOB
class Job(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(default=0)
    native_platform_id_list = models.CommaSeparatedIntegerField(max_length=255)
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
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            resource['datetime_from'] = utc_datetime_to_utc_string(self.datetime_from)
            resource['datetime_to'] = utc_datetime_to_utc_string(self.datetime_to)
            if self.name == '(native job)':
                resource['nodes'] = [ n.to_dict(head_only=True) for n in Node.objects.filter(platform__in = Platform.objects.filter(native_id__in = map(int, self.native_platform_id_list.split(',')))) ]
                resource['nodegroups'] = None
            else:
                resource['nodes'] = [ j2n.node.to_dict(head_only=True) for j2n in self.nodes.all() ]
                resource['nodegroups'] = [ ng.to_dict(head_only=True) for ng in self.nodegroups.all() ]
            resource['node_count'] = len(resource['nodes'])
        return resource

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = verbose_name +'s'
    
# NODE
class Node(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField()
    name = models.CharField(max_length=255)
    platform = models.ForeignKey(Platform, verbose_name='Platform')
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
        resource['id'] = self.id
        if not head_only:
            resource['platform'] = build_url(server_url = FEDERATION_URL, path = self.platform.get_absolute_url())
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
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    job = models.ForeignKey(Job, related_name='nodegroups', verbose_name='Job')
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/nodegroups/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            resource['nodes'] = [ ng2n.node.to_dict(head_only=True) for ng2n in self.nodes.all()]
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
        
        

