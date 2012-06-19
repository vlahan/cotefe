import os

from collections import OrderedDict
from django.db import models

from testbed_abstraction import config, utils

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
        return self.id

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.FEDERATION_SERVER_URL, 'platforms', self.id)
    
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['id'] = self.id
        resource['uri'] = self.get_absolute_url()
        resource['media_type'] = config.MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        verbose_name = 'Platform'
        verbose_name_plural = verbose_name +'s'
        



#def update_filename(instance, filename):
#    filepath = 'images'
#    filename = instance.id
#    return os.path.join(filepath, filename)
#
# class Image(Resource):
#    id = models.CharField(max_length=255, primary_key=True)
#    name = models.CharField(max_length=255)
#    description = models.TextField()
#    file = models.FileField(upload_to=update_filename, null=True, blank=True)
#    
#    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
#    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='Modified')
#
#    def __unicode__(self):
#        return self.name
#
#    def get_absolute_url(self):
#        return "/images/%s" % self.id
#
#    def to_dict(self, head_only = False):
#        resource = OrderedDict()
#        resource['uri'] = build_url(path = self.get_absolute_url())
#        resource['media_type'] = MEDIA_TYPE
#        resource['name'] = self.name
#        resource['id'] = self.id
#        if not head_only:
#            resource['description'] = self.description
#            if self.file:
#                resource['download'] = build_url(path = '/uploads/' + self.file.name)
#                resource['upload'] = build_url(path = '%s/upload' % self.get_absolute_url())
#            else:
#                resource['download'] = None
#                resource['upload'] = build_url(path = '%s/upload' % self.get_absolute_url())
#            resource['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
#            resource['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
#        return resource
#
#    class Meta:
#        verbose_name = "Image"
#        verbose_name_plural = verbose_name +'s'

# class Job(Resource):
#    id = models.CharField(max_length=255, primary_key=True)
#    native_id = models.IntegerField(default=0)
#    native_platform_id_list = models.CommaSeparatedIntegerField(max_length=255)
#    name = models.CharField(max_length=255)
#    description = models.TextField()
#    datetime_from = models.DateTimeField()
#    datetime_to = models.DateTimeField()
#    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
#    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
#
#    def __unicode__(self):
#        return self.id
#
#    def get_absolute_url(self):
#        return "/jobs/%s" % self.id
#
#    def to_dict(self, head_only = False):
#        r = OrderedDict()
#        r['uri'] = build_url(path = self.get_absolute_url())
#        r['media_type'] = MEDIA_TYPE
#        r['name'] = self.name
#        r['id'] = self.id
#        if not head_only:
#            r['description'] = self.description
#            r['datetime_from'] = utc_datetime_to_utc_string(self.datetime_from)
#            r['datetime_to'] = utc_datetime_to_utc_string(self.datetime_to)
#            if self.name == '(native job)':
#                r['nodes'] = [ n.to_dict(head_only=True) for n in Node.objects.filter(platform__in = Platform.objects.filter(native_id__in = map(int, self.native_platform_id_list.split(',')))) ]
#                r['nodegroups'] = None
#            else:
#                r['nodes'] = [ j2n.node.to_dict(head_only=True) for j2n in self.nodes.all() ]
#                r['nodegroups'] = [ ng.to_dict(head_only=True) for ng in self.nodegroups.all() ]
#            r['node_count'] = len(r['nodes'])
#            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
#            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
#        return r
#
#    class Meta:
#        verbose_name = "Job"
#        verbose_name_plural = verbose_name +'s'

class Node(Resource):
    
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    
    native_id = models.IntegerField(null=True, blank=True)
    
    # list of features advertised by the node
    platform = models.ForeignKey(Platform)
    # sensors = models.ManyToManyField(Sensor)
    # actuators = models.ManyToManyField(Actuator)
    # interfaces = models.ManyToManyField(Interface)
    
    # image = models.ForeignKey(Image, null=True, blank=True)
    
    location_x = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Location X')
    location_y = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Location Y')
    location_z = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Location Z')
    
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return '%s/%s/%s' % (config.SERVER_URL, 'nodes', self.id)
    
    def to_dict(self, head_only = False):
        resource = OrderedDict()
        resource['id'] = self.id
        resource['uri'] = self.get_absolute_url()
        resource['media_type'] = config.MEDIA_TYPE
        resource['name'] = self.name
        if not head_only:
            resource['platform'] = self.platform.to_dict(head_only=True)
            resource['channels'] = [ ch.to_dict(head_only=True) for ch in self.channels.all() ]
            # resource['sensors'] = [ s.to_dict(head_only=True) for s in self.sensors.all() ]
            # resource['actuators'] = [ a.to_dict(head_only=True) for a in self.actuators.all() ]
            # resource['interfaces'] = [ i.to_dict(head_only=True) for i in self.interfaces.all() ]
            # resource['serial_tunnel'] = 'ssh://twistextern@www.twist.tu-berlin.de:%d' % (9000+self.native_id)
            resource['location_x'] = str(self.location_x)
            resource['location_y'] = str(self.location_y)
            resource['location_z'] = str(self.location_z)
            resource['datetime_created'] = utils.local_datetime_to_utc_string(self.datetime_created)
            resource['datetime_modified'] = utils.local_datetime_to_utc_string(self.datetime_modified)
        return resource

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = verbose_name +'s'
        
        
class Channel(Resource):
    
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)    
    node = models.ForeignKey(Node, related_name='channels')
    is_sensor = models.BooleanField()
    is_actuator= models.BooleanField()
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "%s/%s/%s" % (self.node.get_absolute_url(), 'channels', self.id.split(':')[-1])
    
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
        return r
    
    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = verbose_name +'s'
    

class Parameter(Resource):
    id = models.CharField(max_length=255, primary_key=True)    
    channel = models.ForeignKey(Channel, related_name='parameters')
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
        r['id']= self.id
        r['name']=self.name
        r['value']=self.value
        r['media_type'] = config.MEDIA_TYPE
        r['uri'] = self.get_absolute_url()
        if not head_only:
            r['type']=self.type
            r['unit']=self.unit
            r['min']=self.min
            r['max']=self.max
            r['channel']=self.channel.to_dict(head_only=True)
        return r
        

#class NodeGroup(Resource):
#    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
#    name = models.CharField(max_length=255, verbose_name='Name')
#    description = models.TextField(verbose_name='Description')
#    job = models.ForeignKey(Job, related_name='nodegroups', verbose_name='Job')
#    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image')
#    # datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
#    # datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
#    
#    def __unicode__(self):
#        return self.name
#
#    def get_absolute_url(self):
#        return "/nodegroups/%s" % self.id
#
#    def to_dict(self, head_only = False):
#        r = OrderedDict()
#        r['uri'] = build_url(path = self.get_absolute_url())
#        r['media_type'] = MEDIA_TYPE
#        r['name'] = self.name
#        r['id'] = self.id
#        if not head_only:
#            r['description'] = self.description
#            r['nodes'] = [ ng2n.node.to_dict(head_only=True) for ng2n in self.nodes.all()]
#            if self.image:
#                r['image'] = build_url(path = self.image.get_absolute_url())
#            else:
#                r['image'] = None
#            # r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
#            # r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
#        return r
#        
#    class Meta:
#        verbose_name = "NodeGroup"
#        verbose_name_plural = verbose_name +'s'
        


#class Status(Resource):
#    id = models.CharField(max_length=255, primary_key=True)
#    status = models.CharField(max_length=255)
#    http_request = models.TextField()
#    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
#    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
#
#    def __unicode__(self):
#        return self.id
#
#    def get_absolute_url(self):
#        return "/status/%s" % self.id
#
#    def to_dict(self, head_only = False):
#        r = OrderedDict()
#        r['uri'] = build_url(path = self.get_absolute_url())
#        r['media_type'] = MEDIA_TYPE
#        r['id'] = self.id
#        r['http_request'] = self.http_request
#        r['status'] = self.status
#        r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
#        r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
#        return r
#    
#    class Meta:
#        verbose_name = "Status"
#        verbose_name_plural = verbose_name +'es'    
