from collections import OrderedDict
from django.db import models

from testbed_abstraction import config, utils

class Resource(models.Model):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='Id', default=utils.generate_id)
    name = models.CharField(max_length=255, verbose_name='Name')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='Modified')
    
    # resource_path_url = 'default'
    # verbose_name = 'Default'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.SERVER_URL, self.resource_path_url, self.id)

    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['uri'] = self.get_absolute_url()
        resource['media_type'] = config.MEDIA_TYPE
        resource['name'] = self.name
        resource['id'] = self.id
        if not head_only:
            resource['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        abstract = True

class Node(Resource):
    resource_path_url = 'nodes'
    
class Job(Resource):
    resource_path_url = 'jobs'
    
class Image(Resource):
    resource_path_url = 'images'
    
class User(Resource):
    resource_path_url = 'users'
    
    