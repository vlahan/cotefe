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
        
# TESTBED ADAPTATION API RESOURCES

class TestbedResource(AbstractResource):
    organization = models.CharField(max_length=255)
    
class ImageResource(AbstractResource):
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User)
    image_format = models.ForeignKey(ImageFormatResource)
    file = models.FileField(upload_to='images/')
    mapping_keys = models.CharField(max_length=255)
    mapping_values = models.CharField(max_length=255)

class JobResource(AbstractResource):
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User)

class TaskResource(AbstractResource):
    pass

class TraceResource(AbstractResource):
    pass

class LogResource(AbstractResource):
    pass

class Node(AbstractResource):
    power = models.BooleanField(default=False)

class NodeGroup(AbstractResource):
    nodes = models.ManyToManyField(Node)
    
class Socket(AbstractResource):
    pass

# READ-ONLY RESOUCES

class SensorResource(AbstractResource):
    pass

class ActuatorResource(AbstractResource):
    pass

class RadioResource(AbstractResource):
    pass

class InterfaceResource(AbstractResource):
    pass

class ImageFormatResource(AbstractResource):
    pass


    
class PlatformResource(AbstractResource):
    pass


    





    
class Mobility(AbstractResource):
    pass


    
class Status(AbstractResource):
    pass