from django.contrib import admin

from api.models import *

admin.site.register(Platform)
# admin.site.register(Interface)
# admin.site.register(Sensor)
# admin.site.register(Actuator)
admin.site.register(Channel)

admin.site.register(Node)

admin.site.register(NodeGroup)

admin.site.register(Image)
admin.site.register(Job)
admin.site.register(Status)
