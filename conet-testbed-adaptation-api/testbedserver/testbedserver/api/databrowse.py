from django.contrib import databrowse
from testbedserver.api.models import *

databrowse.site.register(Testbed)
databrowse.site.register(Platform)
databrowse.site.register(Node)
databrowse.site.register(NodeGroup)
databrowse.site.register(NodeGroup2Node)
databrowse.site.register(Image)