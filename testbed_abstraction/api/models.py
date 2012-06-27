from collections import OrderedDict
from django.db import models
from api import config, utils

class Resource(models.Model):
    
    class Meta:
        abstract = True


class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    native_id = models.IntegerField(null=True, blank=True)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.FEDERATION_SERVER_URL, 'platforms', self.id)
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id'] = self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
class Node(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    native_id = models.IntegerField(null=True, blank=True)
    platform = models.ForeignKey('api.Platform')
    image = models.ForeignKey('api.Image', null=True, blank=True)
    location_x = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    location_y = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    location_z = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.SERVER_URL, 'nodes', self.id)
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id'] = self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['platform'] = self.platform.to_dict(head_only=True)
            r['channels'] = [ ch.to_dict(head_only=True) for ch in self.channels.all() ]
            if self.native_id:
                r['serial_tunnel'] = 'ssh://twistextern@www.twist.tu-berlin.de:%d' % (9000+self.native_id)
            r['location_x'] = str(self.location_x)
            r['location_y'] = str(self.location_y)
            r['location_z'] = str(self.location_z)
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
class Channel(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)    
    node = models.ForeignKey('api.Node', related_name='channels')
    is_sensor = models.BooleanField()
    is_actuator= models.BooleanField()
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '%s/%s/%s' % (self.node.get_absolute_url(), 'channels', self.id.split(':')[-1])
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id'] = self.id.split(':')[-1]
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['is_sensor'] = self.is_sensor
            r['is_actuator'] = self.is_actuator
            r['node'] = self.node.to_dict(head_only=True)
            r['parameters'] = [ p.to_dict(head_only=True) for p in self.parameters.all() ]
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
class Parameter(Resource):
    id = models.CharField(max_length=255, primary_key=True)    
    channel = models.ForeignKey('api.Channel', related_name='parameters')
    name = models.CharField(max_length=255)    
    value = models.FloatField(max_length=255)
    type = models.CharField(max_length=255)      
    unit = models.CharField(max_length=255)
    min = models.FloatField(max_length=255)  
    max = models.FloatField(max_length=255)  

    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "%s/%s/%s" % (self.channel.get_absolute_url(), 'parameters', self.id.split(':')[-1])

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id']= self.id.split(':')[-1]
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name']=self.name
        if not head_only:
            r['type']=self.type
            r['value']=self.value
            r['unit']=self.unit
            r['min']=self.min
            r['max']=self.max
            r['channel']=self.channel.to_dict(head_only=True)
            r['node']=self.channel.node.to_dict(head_only=True)
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
class Job(Resource):
    id = models.CharField(max_length=255, primary_key=True, default=utils.generate_id)
    native_id = models.IntegerField(null=True, blank=True)
    native_platform_id_list = models.CommaSeparatedIntegerField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    nodes = models.ManyToManyField('api.Node', related_name='jobs')
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.SERVER_URL, 'jobs', self.id)
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id'] = self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['datetime_from'] = utils.local_datetime_to_utc_string(self.datetime_from)
            r['datetime_to'] = utils.local_datetime_to_utc_string(self.datetime_to)
            if self.name == '(native job)':
                r['nodes'] = [ n.to_dict(head_only=True) for n in Node.objects.filter(platform__in = Platform.objects.filter(native_id__in = map(int, self.native_platform_id_list.split(',')))) ]
            else:
                r['nodes'] = [ n.to_dict(head_only=True) for n in self.nodes.all() ]
            r['node_count'] = len(r['nodes'])
            r['nodegroups'] = [ ng.to_dict(head_only=True) for ng in self.nodegroups.all() ]
            r['images'] = [ i.to_dict(head_only=True) for i in self.images.all() ]
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
class NodeGroup(Resource):
    id = models.CharField(max_length=255, primary_key=True, default=utils.generate_id)
    name = models.CharField(max_length=255)
    description = models.TextField()
    job = models.ForeignKey('api.Job', related_name='nodegroups')
    nodes = models.ManyToManyField('api.Node', related_name='nodegroups')
    image = models.ForeignKey('api.Image', null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        # return '%s/%s/%s/%s/%s' % (config.SERVER_URL, 'jobs', self.job.id, 'nodegroups', self.id)
        return '%s/%s/%s' % (config.SERVER_URL, 'nodegroups', self.id)

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id']= self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name']=self.name
        if not head_only:
            r['description'] = self.description
            r['nodes'] = [ n.to_dict(head_only=True) for n in self.nodes.all()]
            if self.image:
                r['image'] = self.image.get_absolute_url()
            else:
                r['image'] = None
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    

class Image(Resource):
    id = models.CharField(max_length=255, primary_key=True, default=utils.generate_id)
    name = models.CharField(max_length=255)
    description = models.TextField()
    job = models.ForeignKey('api.Job', related_name='images')
    file = models.FileField(upload_to=utils.update_filename, null=True, blank=True)
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.SERVER_URL, 'images', self.id)
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id'] = self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name'] = self.name
        if not head_only:
            r['description'] = self.description
            r['upload'] = '%s/upload' % self.get_absolute_url()
            # r['download'] = '%s/download' % self.get_absolute_url()
            if self.file:
                r['download'] = '%s/static/%s' % (config.SERVER_URL,  self.file.name)
            else:
                r['download'] = None
            r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r
    
    
class Status(Resource):
    id = models.CharField(max_length=255, primary_key=True, default=utils.generate_id)
    status = models.CharField(max_length=255)
    http_request = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.id
    
    def get_absolute_url(self):
        return "%s/%s/%s" % (config.SERVER_URL, 'status', self.id)

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['id']= self.id
        r['uri'] = self.get_absolute_url()
        r['media_type'] = config.MEDIA_TYPE
        r['name']=self.name
        r['http_request'] = self.http_request
        r['status'] = self.status
        r['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
        r['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return r 