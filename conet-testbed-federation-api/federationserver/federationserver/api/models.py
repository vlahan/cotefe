from django.db import models
from django.contrib.auth.models import User

try:
    from federationserver.settings import *
    from federationserver.utils import *
except ImportError:
    from settings import *
    from utils import *


class Resource(models.Model):
    class Meta:
        abstract = True


class Federation(Resource):
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    
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
            resource['description'] = self.description
            resource['testbeds'] = build_url(path = '/testbeds/')
            resource['platforms'] = build_url(path = '/platforms/')
            resource['projects'] = build_url(path = '/projects/')
            resource['experiments'] = build_url(path = '/experiments/')
            resource['property_sets'] = build_url(path = '/property-sets/')
            resource['virtual_nodes'] = build_url(path = '/virtual-nodes/')
            resource['virtual_nodegroups'] = build_url(path = '/virtual-nodegroups/')
            resource['virtual_tasks'] = build_url(path = '/virtual-tasks/')
            resource['images'] = build_url(path = '/images/')
        return resource
        
    class Meta:
        verbose_name = "Federation"
        verbose_name_plural = verbose_name


class Project(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/projects/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            resource['experiments'] = [ experiment.to_dict(head_only = True) for experiment in self.experiments.all() ]
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = verbose_name +'s'


class Experiment(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    project = models.ForeignKey(Project, verbose_name='Project', related_name='experiments', on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/experiments/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            resource['project'] = build_url(path = self.project.get_absolute_url())
            resource['property_sets'] = [ ps.to_dict(head_only = True) for ps in self.property_sets.all() ]
            resource['virtual_nodes'] = [ vn.to_dict(head_only = True) for vn in self.virtual_nodes.all() ]
            resource['node_count'] = len(resource['virtual_nodes'])
            resource['virtual_nodegroups'] = [ vng.to_dict(head_only = True) for vng in self.virtual_nodegroups.all() ]
            resource['images'] = [ i.to_dict(head_only = True) for i in self.images.all() ]
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource
    
    class Meta:
        verbose_name = "Experiment"
        verbose_name_plural = verbose_name +'s'
        

class Testbed(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    organization = models.CharField(max_length=255, verbose_name='Organization')
    description = models.TextField(verbose_name='Description')
    url = models.URLField(verbose_name='URL')
    node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/testbeds/%s" % self.id
        
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['organization'] = self.organization
            resource['description'] = self.description
            resource['url'] = self.url
            resource['node_count'] = self.node_count
            resource['node_count_per_platform'] = [ { "platform" : t2p.platform.to_dict(head_only=True), "node_count" : t2p.node_count } for t2p in self.platforms.all()]

        return resource
        
    class Meta:
        verbose_name = "Testbed"
        verbose_name_plural = verbose_name +'s'


class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Created')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/platforms/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
        return resource

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = verbose_name +'s'

class Image(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    experiment = models.ForeignKey(Experiment, related_name='images', verbose_name='Experiment')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
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
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'

class PropertySet(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    experiment = models.ForeignKey(Experiment, related_name='property_sets', verbose_name='Experiment')
    platform = models.ForeignKey(Platform, verbose_name='Platform')
    node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/property-sets/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['experiment'] = build_url(path = self.experiment.get_absolute_url())
            resource['description'] = self.description
            resource['platform'] = build_url(path = self.platform.get_absolute_url())
            resource['node_count'] = self.node_count
            resource['virtual_nodes'] = [ virtual_node.to_dict(head_only = True) for virtual_node in self.virtual_nodes.all() ]
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        verbose_name = "Property Set"
        verbose_name_plural = verbose_name +'s'
        

class VirtualNode(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    platform = models.ForeignKey(Platform, related_name='virtual_nodes', verbose_name='Platform')
    experiment = models.ForeignKey(Experiment, related_name='virtual_nodes', verbose_name='Experiment')
    property_set = models.ForeignKey(PropertySet, related_name='virtual_nodes', verbose_name='PropertySet')
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/virtual-nodes/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        resource['property_set'] = build_url(path = self.property_set.get_absolute_url())
        if not head_only:
            resource['platform'] = build_url(path = self.platform.get_absolute_url())
            resource['experiment'] = build_url(path = self.experiment.get_absolute_url())
            if self.image:
                resource['image'] = build_url(path = self.image.get_absolute_url())
            else:
                resource['image'] = None
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource
    
    class Meta:
        verbose_name = "Virtual Node"
        verbose_name_plural = verbose_name +'s'


class VirtualNodeGroup(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    experiment = models.ForeignKey(Experiment, related_name='virtual_nodegroups', verbose_name='Experiment')
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/virtual-nodegroups/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['description'] = self.description
            resource['experiment'] = build_url(path = self.experiment.get_absolute_url())
            resource['virtual_nodes'] = [ vng2vn.virtual_node.to_dict(head_only=True) for vng2vn in self.virtual_nodes.all()]
            resource['node_count'] = len(resource['virtual_nodes'])
            if self.image:
                resource['image'] = build_url(path = self.image.get_absolute_url())
            else:
                resource['image'] = None
            resource['datetime_created'] = utc_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utc_datetime_to_utc_string(self.datetime_modified)
        return resource
        
    class Meta:
        verbose_name = "Virtual NodeGroup"
        verbose_name_plural = verbose_name +'s'
        
# AUXILIARY TABLES
class VirtualNodeGroup2VirtualNode(models.Model):
    virtual_nodegroup = models.ForeignKey(VirtualNodeGroup, verbose_name='VirtualNodeGroup', related_name='virtual_nodes')
    virtual_node = models.ForeignKey(VirtualNode, verbose_name='VirtualNode', related_name='virtual_nodegroups')
    
    def __unicode__(self):
        return u'%s %s' % (self.virtual_nodegroup, self.virtual_node)
    
    class Meta:
        verbose_name = "VirtualNodeGroup2VirtualNode"
        verbose_name_plural = verbose_name +'s'

class Testbed2Platform(models.Model):
    testbed = models.ForeignKey(Testbed, related_name='platforms', verbose_name='Testbed')
    platform = models.ForeignKey(Platform, related_name='testbeds',verbose_name='Platform')
    node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    
    def __unicode__(self):
        return '%s %s' % (self.testbed, self.platform)
    
    class Meta:
        verbose_name = "Testbed2Platform"
        verbose_name_plural = verbose_name +'s'

