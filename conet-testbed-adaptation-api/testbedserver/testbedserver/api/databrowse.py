from django.contrib import databrowse
from testbedserver.api.models import *

databrowse.site.register(User)

# databrowse.site.register(Federation)
# databrowse.site.register(Project)
# databrowse.site.register(Experiment)
# databrowse.site.register(PropertySet)
# databrowse.site.register(VirtualNode)
# databrowse.site.register(VirtualNodeGroup)
# databrowse.site.register(VirtualTask)

databrowse.site.register(Testbed)
databrowse.site.register(Platform)
databrowse.site.register(Job)
databrowse.site.register(Node)
databrowse.site.register(NodeGroup)
databrowse.site.register(Task)
databrowse.site.register(Trace)
databrowse.site.register(Log)