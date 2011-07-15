from django.db import models
from django.contrib.auth.models import User
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
        return '/'
        
    def to_dict(self):
        r = dict()
        r['uri'] = build_url()
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['description'] = self.description
        r['testbeds'] = build_url(path = '/testbeds/')
        r['platforms'] = build_url(path = '/platforms/')
        r['projects'] = build_url(path = '/projects/')
        r['experiments'] = build_url(path = '/experiments/')
        r['jobs'] = build_url(path = '/jobs/')
        return r
        
    class Meta:
        verbose_name = 'Federation'
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
        return '/projects/%s' % (self.id, )

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if head_only:
            r['experiment_count'] = len([ experiment.to_dict() for experiment in self.experiments.all() ])
        if not head_only:
            r['description'] = self.description
            r['experiments'] = [ experiment.to_dict(head_only = True) for experiment in self.experiments.all() ]
            r['experiment_count'] = len(r['experiments'])
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = verbose_name +'s'


class Experiment(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    project = models.ForeignKey(Project, verbose_name='Project', related_name='experiments', on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/experiments/%s' % (self.id, )

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if head_only:
            r['virtual_node_count'] = len([ vn.to_dict(head_only = True) for vn in self.virtual_nodes.all() ])
        if not head_only:
            r['description'] = self.description
            r['project'] = build_url(path = self.project.get_absolute_url())
            r['property_sets'] = [ ps.to_dict(head_only = True) for ps in self.property_sets.all() ]
            r['virtual_nodes'] = [ vn.to_dict(head_only = True) for vn in self.virtual_nodes.all() ]
            r['virtual_node_count'] = len(r['virtual_nodes'])
            r['virtual_nodegroups'] = [ vng.to_dict(head_only = True) for vng in self.virtual_nodegroups.all() ]
            r['images'] = [ i.to_dict(head_only = True) for i in self.images.all() ]
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r
    
    class Meta:
        verbose_name = 'Experiment'
        verbose_name_plural = verbose_name +'s'
        

class Testbed(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    organization = models.CharField(max_length=255, verbose_name='Organization')
    description = models.TextField(verbose_name='Description')
    server_url = models.URLField(verbose_name='URL')
    node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/testbeds/%s' % (self.id, )
        
    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['organization'] = self.organization
            r['description'] = self.description
            r['server_url'] = self.server_url
            r['node_count'] = self.node_count
            # r['node_count_per_platform'] = [ { 'platform' : t2p.platform.to_dict(head_only=True), 'node_count' : t2p.node_count } for t2p in self.platforms.all()]
            r['platforms'] = [ t2p.platform.to_dict(head_only = True) for t2p in self.platforms.all() ]
            r['jobs'] = [ j.to_dict(head_only = True) for j in self.jobs.all() ]
        return r
        
    class Meta:
        verbose_name = 'Testbed'
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
        return '/platforms/%s' % (self.id, )

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
        return r

    class Meta:
        verbose_name = 'Platform'

class PropertySet(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    experiment = models.ForeignKey(Experiment, related_name='property_sets', verbose_name='Experiment', on_delete=models.PROTECT)
    platform = models.ForeignKey(Platform, verbose_name='Platform', on_delete=models.PROTECT)
    virtual_node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/experiments/%s/property-sets/%s' % (self.experiment.id, self.id)

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if head_only:
            r['virtual_node_count'] = len([ virtual_node.to_dict(head_only = True) for virtual_node in self.virtual_nodes.all() ])
        if not head_only:
            r['experiment'] = build_url(path = self.experiment.get_absolute_url())
            r['description'] = self.description
            r['platform'] = build_url(path = self.platform.get_absolute_url())
            r['virtual_nodes'] = [ virtual_node.to_dict(head_only = True) for virtual_node in self.virtual_nodes.all() ]
            r['virtual_node_count'] = len(r['virtual_nodes'])
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = 'Property Set'
        verbose_name_plural = verbose_name +'s'
        
        
def update_filename(instance, filename):
    filepath = 'uploads/images'
    filename = instance.id
    return os.path.join(filepath, filename)

class Image(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    experiment = models.ForeignKey(Experiment, related_name='images', verbose_name='Experiment', on_delete=models.PROTECT)
    file = models.FileField(upload_to=update_filename, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/experiments/%s/images/%s' % (self.experiment.id, self.id)

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            r['experiment'] = build_url(path = self.experiment.get_absolute_url()) 
        return r

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = verbose_name +'s'
        

class VirtualNode(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    platform = models.ForeignKey(Platform, related_name='virtual_nodes', verbose_name='Platform', on_delete=models.PROTECT)
    experiment = models.ForeignKey(Experiment, related_name='virtual_nodes', verbose_name='Experiment', on_delete=models.PROTECT)
    property_set = models.ForeignKey(PropertySet, related_name='virtual_nodes', verbose_name='PropertySet', on_delete=models.PROTECT)
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image', on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return '/experiments/%s/virtual-nodes/%s' % (self.experiment.id, self.id)

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['property_set'] = build_url(path = self.property_set.get_absolute_url())
            r['platform'] = build_url(path = self.platform.get_absolute_url())
            r['experiment'] = build_url(path = self.experiment.get_absolute_url())
            if self.image:
                r['image'] = build_url(path = self.image.get_absolute_url())
            else:
                r['image'] = None
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r
    
    class Meta:
        verbose_name = 'Virtual Node'
        verbose_name_plural = verbose_name +'s'
        

class VirtualNodeGroup(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    experiment = models.ForeignKey(Experiment, related_name='virtual_nodegroups', verbose_name='Experiment', on_delete=models.PROTECT)
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image', on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/experiments/%s/virtual-nodegroups/%s' % (self.experiment.id, self.id)

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if head_only:
            r['virtual_node_count'] = len([ vng2vn.virtual_node.to_dict(head_only = True) for vng2vn in self.virtual_nodes.all()])
        if not head_only:
            r['description'] = self.description
            r['experiment'] = build_url(path = self.experiment.get_absolute_url())
            r['virtual_nodes'] = [ vng2vn.virtual_node.to_dict(head_only = True) for vng2vn in self.virtual_nodes.all()]
            r['virtual_node_count'] = len(r['virtual_nodes'])
            if self.image:
                r['image'] = build_url(path = self.image.get_absolute_url())
            else:
                r['image'] = None
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r
        
    class Meta:
        verbose_name = 'Virtual NodeGroup'
        verbose_name_plural = verbose_name +'s'
        

class VirtualTask(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    method = models.CharField(max_length=10)
    target = models.URLField()
    payload = models.TextField()
    experiment = models.ForeignKey(Experiment, related_name='virtual_tasks', verbose_name='Experiment', on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return '/experiments/%s/virtual-tasks/%s' % (self.experiment.id, self.id)

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            r['method'] = self.method
            r['target'] = self.target
            r['experiment'] = build_url(path = self.experiment.get_absolute_url())
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = 'Virtual Task'
        verbose_name_plural = verbose_name +'s'

class Job(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    testbed = models.ForeignKey(Testbed, related_name='jobs', verbose_name='Testbed', on_delete=models.PROTECT)
    experiment = models.ForeignKey(Experiment, blank=True, null=True, related_name='jobs', verbose_name='Experiment', on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return '/jobs/%s' % (self.id, )

    def to_dict(self, head_only = False):
        r = dict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            r['datetime_from'] = utc_datetime_to_utc_string(self.datetime_from)
            r['datetime_to'] = utc_datetime_to_utc_string(self.datetime_to)
            r['testbed'] = build_url(path = self.testbed.get_absolute_url())
            if self.experiment:
                r['experiment'] = build_url(path = self.experiment.get_absolute_url())
            else:
                r['experiment'] = None
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = verbose_name +'s'
        
        
class VirtualNodeGroup2VirtualNode(models.Model):
    virtual_nodegroup = models.ForeignKey(VirtualNodeGroup, verbose_name='VirtualNodeGroup', related_name='virtual_nodes', on_delete=models.PROTECT)
    virtual_node = models.ForeignKey(VirtualNode, verbose_name='VirtualNode', related_name='virtual_nodegroups', on_delete=models.PROTECT)
    
    def __unicode__(self):
        return u'%s %s' % (self.virtual_nodegroup, self.virtual_node)
    
    class Meta:
        verbose_name = 'VirtualNodeGroup2VirtualNode'
        verbose_name_plural = verbose_name +'s'

class Testbed2Platform(models.Model):
    testbed = models.ForeignKey(Testbed, related_name='platforms', verbose_name='Testbed', on_delete=models.PROTECT)
    platform = models.ForeignKey(Platform, related_name='testbeds',verbose_name='Platform', on_delete=models.PROTECT)
    node_count = models.IntegerField(default=0, verbose_name='Number of Nodes')
    
    def __unicode__(self):
        return '%s %s' % (self.testbed, self.platform)
    
    class Meta:
        verbose_name = 'Testbed2Platform'
        verbose_name_plural = verbose_name +'s'
        
#class Job2Node(models.Model):
#    job = models.ForeignKey(Job, verbose_name='Job', related_name='nodes')
#    node = models.ForeignKey(Node, verbose_name='Node', related_name='jobs')
#    
#    def __unicode__(self):
#        return u'%s %s' % (self.job, self.node)
#    
#    class Meta:
#        verbose_name = 'Job2Node'
#        verbose_name_plural = verbose_name +'s'
