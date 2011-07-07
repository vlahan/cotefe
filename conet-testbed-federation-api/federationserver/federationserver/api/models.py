from django.db import models
from django.contrib.auth.models import User
from federationserver.settings import *
from federationserver.utils import *

# RESOURCE ABSTRACT MODEL
class Resource(models.Model):
    class Meta:
        abstract = True
        
# FEDERATION
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
            resource['platforms'] = build_url(path = '/platforms/')
            resource['projects'] = build_url(path = '/projects/')
            resource['experiments'] = build_url(path = '/experiments/')
            resource['testbeds'] = build_url(path = '/testbeds/')
        return resource
        
    class Meta:
        verbose_name = "Federation"
        verbose_name_plural = verbose_name


# PROJECT
class Project(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/projects/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
            resource['experiments'] = [ experiment.to_dict(head_only = True) for experiment in self.experiments.all() ]
        return resource

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = verbose_name +'s'
    
# NODE
class Experiment(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    project = models.ForeignKey(Project, verbose_name='Project', related_name='experiments')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/experiments/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
            resource['project'] = build_url(path = self.project.get_absolute_url())
        return resource
    
    class Meta:
        verbose_name = "Experiment"
        verbose_name_plural = verbose_name +'s'
        
# TESTBED
class Testbed(Resource):
    id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    organization = models.CharField(max_length=255, blank=True, null=True, verbose_name='Organization')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    url = models.URLField(verbose_name='URL')
    node_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/testbeds/%s" % self.id
        
    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['organization'] = self.organization
            resource['description'] = self.description
            resource['url'] = self.url
            resource['node_count'] = self.node_count
            resource['node_count_per_platform'] = [ { "platform" : t2p.platform.to_dict(head_only=True), "node_count" : t2p.node_count } for t2p in self.platforms.all()]

        return resource
        
    class Meta:
        verbose_name = "Testbed"
        verbose_name_plural = verbose_name

# PLATFORM
class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/platforms/%s" % self.id

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['id'] = self.id
            resource['description'] = self.description
        return resource

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = verbose_name +'s'
        
# AUXILIARY TABLES

class Testbed2Platform(models.Model):
    testbed = models.ForeignKey(Testbed, related_name='platforms', verbose_name='Testbed')
    platform = models.ForeignKey(Platform, related_name='testbeds',verbose_name='Platform')
    node_count = models.IntegerField()
    
    def __unicode__(self):
        return '%s %s' % (self.testbed, self.platform)
    
    class Meta:
        verbose_name = "Testbed2Platform"
        verbose_name_plural = verbose_name +'s'
