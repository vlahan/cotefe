from django.contrib import admin
from api.models import *

admin.site.register(Platform)

class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'platform', 'native_id', 'location_x', 'location_y', 'location_z')

admin.site.register(Node, NodeAdmin)

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'channel', 'value', 'unit', 'min', 'max')

admin.site.register(Parameter, ParameterAdmin)

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'node', 'is_sensor', 'is_actuator')
    
admin.site.register(Channel, ChannelAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'native_id', 'datetime_from', 'datetime_to')
    
admin.site.register(Job, JobAdmin)

class NodeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'job')
    
admin.site.register(NodeGroup, NodeGroupAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'job', 'file')
    
admin.site.register(Image, ImageAdmin)