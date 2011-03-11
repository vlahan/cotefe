from django.db import models
from django.contrib.auth.models import User

TAA_PROTOCOL = 'http'
TAA_HOST = 'localhost'
TAA_PORT = '8001'

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True
JSON_SORT_KEYS = False

# UTILITY FUNCTIONS

def build_url(protocol = 'http', host = 'localhost', port = '80', path = '/'):
    # path MUST include '/'
    return protocol + '://' + host + ':' + port + path

# TESTBED

class Testbed(models.Model):
    name = models.CharField(max_length=255)
    organization = model.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        slug = str(self.id)
        return "/platforms/%s" % slug
        
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(TAA_PROTOCOL, TAA_HOST, TAA_PORT)
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['platforms'] = resource['uri'] + '/platforms/'
            resource['jobs'] = resource['uri'] + '/jobs/'
        return resource
    
# USER

class User(models.Model):
    user = models.OneToOneField(User)
    organization = models.CharField(max_length=255)
    openid = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.openid
        
    def get_absolute_url(self):
        slug = str(self.id)
        return "/platforms/%s" % slug

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.user.username
        if not head_only:
            resource['email'] = self.user.email
            resource['organization'] = self.organization
            resource['openid'] = self.openid
        return resource

# PLATFORM

class Platform(models.Model):
    name = models.CharField(max_length=255)
    tinyos_name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        slug = str(self.id)
        return "/platforms/%s" % slug
   
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/platforms/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['tiny_os'] = self.tinyos_name
        return resource
        
# JOB

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
        return "/jobs/%s" % slug
   
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/jobs/' + str(self.key().id()))
        resource['media_type'] = MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['testbed'] = build_url(FS_PROTOCOL, FS_HOST, FS_PORT, '/testbeds/' + str(self.testbed.key().id()))
            resource['datetime_from'] = self.datetime_from
            resource['datetime_to'] = self.datetime_to
            resource['uid'] = self.uid
        return resource