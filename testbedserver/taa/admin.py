from django.contrib import admin
from testbedserver.taa.models import *

admin.site.register(Testbed)
admin.site.register(User)
admin.site.register(Platform)
admin.site.register(Job)
admin.site.register(Image)
admin.site.register(Node)
admin.site.register(NodeGroup)