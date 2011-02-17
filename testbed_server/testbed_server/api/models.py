import base64
import hashlib
from django.db import models
#from django.contrib.auth.models import User

#class User(User):
#    openid = models.CharField(max_length=255)
#    
#    def __unicode__(self):
#        return self.openid

class Testbed(models.Model):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/platforms/%s" % slug

    
class Job(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/jobs/%s" % str(self.id)