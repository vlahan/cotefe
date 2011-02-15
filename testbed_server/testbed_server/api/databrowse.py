from django.contrib import databrowse
from api.models import *

databrowse.site.register(Testbed)
databrowse.site.register(Job)
databrowse.site.register(Task)
databrowse.site.register(Trace)
databrowse.site.register(Log)
databrowse.site.register(ImageFormat)
databrowse.site.register(Image)
databrowse.site.register(Platform)
databrowse.site.register(Interface)
databrowse.site.register(Radio)
databrowse.site.register(Sensor)
databrowse.site.register(Actuator)
databrowse.site.register(Mobility)
databrowse.site.register(Node)
databrowse.site.register(NodeGroup)
databrowse.site.register(Socket)
