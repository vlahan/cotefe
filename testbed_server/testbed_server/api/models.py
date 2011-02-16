from django.db import models
from django.contrib.auth.models import User

class AbstractResource(models.Model):
    uri = models.CharField(max_length=255)
    media_type = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        abstract = True

class Testbed(AbstractResource):
    organization = models.CharField(max_length=255)

class Job(AbstractResource):
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User)