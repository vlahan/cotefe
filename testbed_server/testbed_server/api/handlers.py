from piston.handler import BaseHandler
from api.models import *

class TestbedHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Testbed
    
class JobHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Job

class TaskHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Task
        
class TraceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Trace
    
class LogHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Log

class ImageFormatHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ImageFormat

class ImageHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Image

class PlatformHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Platform

class InterfaceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Interface

class RadioHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Radio

class SensorHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Sensor

class ActuatorHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Actuator

class MobilityHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Mobility
    
class NodeHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Node
 
class NodeGroupHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = NodeGroup

class SocketHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Socket
