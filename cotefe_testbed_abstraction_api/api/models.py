from collections import OrderedDict

from django.db import models

class Resource(models.Model):
    
    class Meta:
        abstract = True
        
class OpenIDIdentity(models.Model):
    identifier = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
        
class User(Resource):
    username = models.CharField(max_length=255, primary_key=True)
    # password = models.CharField(max_length=255, primary_key=True)
    first = models.CharField(max_length=255, primary_key=True)
    last = models.CharField(max_length=255, primary_key=True)
    email = db.StringProperty()
    organization = db.StringProperty()
    admin = db.BooleanProperty()
    datetime_created = db.DateTimeProperty(auto_now_add=True)
    datetime_modified = db.DateTimeProperty(auto_now=True)
    
    def id(self):
        return self.key().id()
        
    def uri(self):
        return build_url(path = '/users/%s' % self.id())
    
    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = self.uri()
        r['media_type'] = config.MEDIA_TYPE
        r['username'] = self.username
        r['id'] = self.id()
        if not head_only:
            r['first'] = self.first
            r['last'] = self.last
            r['email'] = self.email
            r['organization'] = self.organization
            r['jobs'] = [ j.to_dict(head_only = True) for j in self.jobs ]
            r['datetime_created'] = convert_datetime_to_string(self.datetime_created)
            r['datetime_modified'] = convert_datetime_to_string(self.datetime_modified)
        return r

class Testbed(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/"
        
    def to_dict(self):
        r = OrderedDict()
        r['uri'] = build_url()
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        r['organization'] = self.organization
        r['description'] = self.description
        r['platforms'] = build_url(path = '/platforms/')
        r['nodes'] = build_url(path = '/nodes/')
        r['nodegroups'] = build_url(path = '/nodegroups/')
        r['jobs'] = build_url(path = '/jobs/')
        r['images'] = build_url(path = '/images/')
        r['background_image'] = build_url(path = '/uploads/testbed/background.jpg')
        r['coordinates_mapping_function_x'] = '-5.5+x*46.9+y*16.6'
        r['coordinates_mapping_function_y'] = '1517-y*16.9-z*78.3'
        return r
        
    class Meta:
        verbose_name = "Testbed"
        verbose_name_plural = verbose_name + 's'

class Platform(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/platforms/%s" % self.id

    def to_dict(self):
        r = OrderedDict()
        r['uri'] = build_url(server_url = FEDERATION_URL, path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        return r

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = verbose_name +'s'

def update_filename(instance, filename):
    filepath = 'images'
    filename = instance.id
    return os.path.join(filepath, filename)

class Image(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to=update_filename, null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/images/%s" % self.id

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            if self.file:
                r['download'] = build_url(path = '/uploads/' + self.file.name)
                r['upload'] = build_url(path = '%s/upload' % self.get_absolute_url())
            else:
                r['download'] = None
                r['upload'] = build_url(path = '%s/upload' % self.get_absolute_url())
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = verbose_name +'s'

class Job(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField(default=0)
    native_platform_id_list = models.CommaSeparatedIntegerField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/jobs/%s" % self.id

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            r['datetime_from'] = utc_datetime_to_utc_string(self.datetime_from)
            r['datetime_to'] = utc_datetime_to_utc_string(self.datetime_to)
            if self.name == '(native job)':
                r['nodes'] = [ n.to_dict(head_only=True) for n in Node.objects.filter(platform__in = Platform.objects.filter(native_id__in = map(int, self.native_platform_id_list.split(',')))) ]
                r['nodegroups'] = None
            else:
                r['nodes'] = [ j2n.node.to_dict(head_only=True) for j2n in self.nodes.all() ]
                r['nodegroups'] = [ ng.to_dict(head_only=True) for ng in self.nodegroups.all() ]
            r['node_count'] = len(r['nodes'])
            r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = verbose_name +'s'

class Node(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    native_id = models.IntegerField()
    name = models.CharField(max_length=255)
    platform = models.ForeignKey(Platform, verbose_name='Platform')
    image = models.ForeignKey(Image, null=True, blank=True)
    location_x = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Location X')
    location_y = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Location Y')
    location_z = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Location Z')

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/nodes/%s" % self.id

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['platform'] = build_url(server_url = FEDERATION_URL, path = self.platform.get_absolute_url())
            if self.image:
                r['image'] = build_url(path = self.image.get_absolute_url())
            else:
                r['image'] = None
            r['serial_tunnel'] = 'ssh://twistextern@www.twist.tu-berlin.de:%d' % (9000+self.native_id)
            r['location_x'] = str(self.location_x)
            r['location_y'] = str(self.location_y)
            r['location_z'] = str(self.location_z)
        return r
    
    class Meta:
        verbose_name = "Node"
        verbose_name_plural = verbose_name +'s'

class NodeGroup(Resource):
    id = models.CharField(max_length=255, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Name')
    description = models.TextField(verbose_name='Description')
    job = models.ForeignKey(Job, related_name='nodegroups', verbose_name='Job')
    image = models.ForeignKey(Image, null=True, blank=True, verbose_name='Image')
    # datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    # datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/nodegroups/%s" % self.id

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['name'] = self.name
        r['id'] = self.id
        if not head_only:
            r['description'] = self.description
            r['nodes'] = [ ng2n.node.to_dict(head_only=True) for ng2n in self.nodes.all()]
            if self.image:
                r['image'] = build_url(path = self.image.get_absolute_url())
            else:
                r['image'] = None
            # r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
            # r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r
        
    class Meta:
        verbose_name = "NodeGroup"
        verbose_name_plural = verbose_name +'s'

class NodeGroup2Node(models.Model):
    nodegroup = models.ForeignKey(NodeGroup, verbose_name='NodeGroup', related_name='nodes')
    node = models.ForeignKey(Node, verbose_name='Node', related_name='nodegroups')
    
    def __unicode__(self):
        return u'%s %s' % (self.nodegroup, self.node)
    
    class Meta:
        verbose_name = "NodeGroup2Node"
        verbose_name_plural = verbose_name +'s'

class Job2Node(models.Model):
    job = models.ForeignKey(Job, verbose_name='Job', related_name='nodes')
    node = models.ForeignKey(Node, verbose_name='Node', related_name='jobs')
    
    def __unicode__(self):
        return u'%s %s' % (self.job, self.node)
    
    class Meta:
        verbose_name = "Job2Node"
        verbose_name_plural = verbose_name +'s'
        


class Status(Resource):
    id = models.CharField(max_length=255, primary_key=True)
    status = models.CharField(max_length=255)
    http_request = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='DateTime Created')
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name='DateTime Modified')

    def __unicode__(self):
        return self.id

    def get_absolute_url(self):
        return "/status/%s" % self.id

    def to_dict(self, head_only = False):
        r = OrderedDict()
        r['uri'] = build_url(path = self.get_absolute_url())
        r['media_type'] = MEDIA_TYPE
        r['id'] = self.id
        r['http_request'] = self.http_request
        r['status'] = self.status
        r['datetime_created'] = berlin_datetime_to_utc_string(self.datetime_created)
        r['datetime_modified'] = berlin_datetime_to_utc_string(self.datetime_modified)
        return r
    
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = verbose_name +'s'