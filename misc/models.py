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
    
# class ImageResource(AbstractResource):
#     description = models.CharField(max_length=255)
#     owner = models.ForeignKey(User)
#     image_format = models.ForeignKey(ImageFormatResource)
#     file = models.FileField(upload_to='images/')

class JobResource(AbstractResource):
    description = models.CharField(max_length=255)
    owner = models.ForeignKey(User)

# class TaskResource(AbstractResource):
#     pass
# 
# class TraceResource(AbstractResource):
#     pass
# 
# class LogResource(AbstractResource):
#     pass
# 
# class NodeResource(AbstractResource):
#     power = models.BooleanField(default=False)
# 
# class NodeGroupResource(AbstractResource):
#     nodes = models.ManyToManyField(Node)
#     
# class SocketResource(AbstractResource):
#     pass

# READ-ONLY RESOUCES

# class SensorResource(AbstractResource):
#     pass
# 
# class ActuatorResource(AbstractResource):
#     pass
# 
# class RadioResource(AbstractResource):
#     pass
# 
# class InterfaceResource(AbstractResource):
#     pass
# 
# class ImageFormatResource(AbstractResource):
#     pass

# class PlatformResource(AbstractResource):
#     pass
# 
# class MobilityResource(AbstractResource):
#     pass
#     
# class StatusResource(AbstractResource):
#     pass