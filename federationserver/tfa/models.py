import logging

# import base64
# import hashlib
from django.db import models
from django.utils import simplejson as json
from django.contrib.auth.models import User
from federationserver.utils.odict import OrderedDict

TFA_PROTOCOL = 'http'
TFA_HOST = 'localhost'
TFA_PORT = '8080'

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True
JSON_SORT_KEYS = False

# UTILITY FUNCTIONS

def build_url(protocol = 'http', host = 'localhost', port = '80', path = '/'):
    # path MUST include '/'
    return protocol + '://' + host + ':' + port + path
    
# MODEL CLASSES

class User(models.Model):
   openid = models.CharField(max_length=255)
   user = models.OneToOneField(User)
   
   def __unicode__(self):
       return self.openid
       
class Federation(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/platforms/%s" % slug
        
    def to_dict(self, head_only = False):
        federation = OrderedDict()
        federation['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT)
        federation['media_type'] = MEDIA_TYPE
        federation['name'] = self.name
        if not head_only:
            federation['testbeds'] = federation['uri'] + '/testbeds/'
            federation['platforms'] = federation['uri'] + '/platforms/'
            federation['jobs'] = federation['uri'] + '/jobs/'
        return federation
        
class Testbed(models.Model):
    # STATIC INFORMATION (INSERTED BY ADMIN)
    protocol = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=255)

    # DYNAMIC FIELDS, RETRIEVED BY HTTP GET ON TESTBED URL
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/testbeds/%s" % slug

    def to_dict(self, head_only = False):
        testbed = OrderedDict()
        testbed['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/' + str(self.key().id()))
        testbed['media_type'] = MEDIA_TYPE
        testbed['name'] = self.name
        if not head_only:
            testbed['organization'] = self.organization
            testbed['platforms'] = testbed['uri'] + '/platforms/'
            testbed['jobs'] = testbed['uri'] + '/jobs/'
        return testbed

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
        
    def to_dict(self, head_only = False):
        platform = OrderedDict()
        platform['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/' + str(self.key().id()))
        platform['media_type'] = MEDIA_TYPE
        platform['name'] = self.name
        if not head_only:
            platform['tiny_os'] = self.tinyos_name
        return platform

    
class Job(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True)
    testbed = models.ForeignKey(Testbed, null=True)
    datetime_from = models.CharField(max_length=25)
    datetime_to = models.CharField(max_length=25)
    platforms = models.ManyToManyField(Platform)
    uid = models.CharField(max_length=25)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        # slug = base64.urlsafe_b64encode(str(self.id))
        # m = hashlib.md5(); m.update(str(self.id)); slug = m.hexdigest()
        return "/jobs/%s" % slug
    
    def to_dict(self, head_only = False):
        job = OrderedDict()
        job['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/jobs/' + str(self.key().id()))
        job['media_type'] = MEDIA_TYPE
        job['name'] = self.name
        if not head_only:
            job['testbed'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/' + str(self.testbed.key().id()))
            job['datetime_from'] = self.datetime_from
            job['datetime_to'] = self.datetime_to
            job['uid'] = self.uid
        return job
