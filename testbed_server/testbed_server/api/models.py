from django.db import models
from django.contrib.auth.models import User

class Testbed(models.Model):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=255)
    native_id = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
class Job(models.Model):
    name = models.CharField(max_length=255)
    native_id = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name