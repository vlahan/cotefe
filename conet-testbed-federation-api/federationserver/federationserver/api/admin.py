from django.contrib import admin

try:
    from federationserver.api.models import *
except ImportError:
    from api.models import *

admin.site.register(Federation)
admin.site.register(Project)
admin.site.register(Experiment)
admin.site.register(Platform)
admin.site.register(Testbed)
admin.site.register(Testbed2Platform)
admin.site.register(PropertySet)
admin.site.register(VirtualNode)
admin.site.register(VirtualNodeGroup)
admin.site.register(VirtualNodeGroup2VirtualNode)
admin.site.register(Image)
