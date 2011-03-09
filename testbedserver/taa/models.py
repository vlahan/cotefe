# import base64
# import hashlib
from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
   openid = models.CharField(max_length=255)
   user = models.OneToOneField(User)
   
   def __unicode__(self):
       return self.openid

class Platform(models.Model):
    name = models.CharField(max_length=255)
    tinyos_name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/platforms/%s" % slug

    
class Job(models.Model):
    name = models.CharField(max_length=255)
    # owner = models.ForeignKey(User, null=True)
    datetime_from = models.CharField(max_length=25)
    datetime_to = models.CharField(max_length=25)
    platforms = models.ManyToManyField(Platform)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/jobs/%s" % slug