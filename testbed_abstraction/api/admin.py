from django.contrib import admin

from api.models import *

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'node', 'is_sensor', 'is_actuator')


class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'platform', 'native_id', 'location_x', 'location_y', 'location_z')


class ParameterAdmin(admin.ModelAdmin):
    # ...
    list_display = ('id', 'name', 'channel', 'value', 'unit', 'min', 'max')

admin.site.register(Platform)
admin.site.register(Node, NodeAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Parameter, ParameterAdmin)
