from django.contrib import admin
from testbedserver.api.models import *

admin.site.register(User)

# admin.site.register(Federation)
# admin.site.register(Project)
# admin.site.register(Experiment)
# admin.site.register(PropertySet)
# admin.site.register(VirtualNode)
# admin.site.register(VirtualNodeGroup)
# admin.site.register(VirtualTask)

admin.site.register(Testbed)
admin.site.register(Platform)
admin.site.register(Job)
admin.site.register(Node)
admin.site.register(NodeGroup)
admin.site.register(Task)
admin.site.register(Trace)
admin.site.register(Log)