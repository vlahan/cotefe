from django.contrib import admin
from testbedserver.api.models import *

admin.site.register(Testbed)
admin.site.register(Platform)
admin.site.register(Node)
admin.site.register(NodeGroup)
admin.site.register(NodeGroup2Node)
admin.site.register(Image)