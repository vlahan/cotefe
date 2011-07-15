from django.contrib import admin

try:
    from api.models import *
except ImportError:
    from testbedserver.api.models import *

admin.site.register(Testbed)
admin.site.register(Platform)
admin.site.register(Node)
admin.site.register(NodeGroup)
admin.site.register(NodeGroup2Node)
admin.site.register(Image)
admin.site.register(Job)
admin.site.register(Job2Node)