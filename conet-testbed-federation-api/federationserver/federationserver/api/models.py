from django.db import models
from django.contrib.auth.models import User
from federationserver.config import *
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
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['projects'] = build_url(path = '/projects/')
            resource['experiments'] = build_url(path = '/experiments/')
        return resource
        
    class Meta:
        verbose_name = "Federation"
        verbose_name_plural = verbose_name +'s'


# PROJECT
class Project(Resource):
    uid = models.CharField(max_length=32, primary_key=True, verbose_name='URI')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/projects/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['experiments'] = [ exp.to_dict(head_only = True) for exp in self.experiments.all() ]
        return resource

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = verbose_name +'s'
    
# NODE
class Experiment(Resource):
    uid = models.CharField(max_length=32, primary_key=True, verbose_name='URI')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    project = models.ForeignKey(Project, verbose_name='Project', related_name='experiments')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/experiments/%s" % self.uid

    def to_dict(self, head_only = False):
        resource = dict()
        resource['uri'] = build_url(path = self.get_absolute_url())
        resource['media_type'] = MEDIA_TYPE
        if not head_only:
            resource['name'] = self.name
            resource['description'] = self.description
            resource['project'] = build_url(path = self.project.get_absolute_url())
        return resource
    
    class Meta:
        verbose_name = "Experiment"
        verbose_name_plural = verbose_name +'s'
        
