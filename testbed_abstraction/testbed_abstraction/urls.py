from django.conf.urls import patterns, include, url

from api.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', testbed_handler),
    
    # url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
        
    url(r'^platforms/$', platform_collection_handler),
        
    url(r'^nodes/$', node_collection_handler),
    # url(r'^nodes/4dd1ba50$', robot_resource_handler),
    url(r'^nodes/(\w+)$', node_resource_handler),
    
    url(r'^nodes/(\w+)/channels/$', node_channel_collection_handler),
    url(r'^nodes/(\w+)/channels/(\w+)$', node_channel_resource_handler),
    
 
    url(r'^nodes/(\w+)/channels/(\w+)/parameters/$', channel_parameter_collection_handler),
    url(r'^nodes/(\w+)/channels/(\w+)/parameters/(\w+)$', channel_parameter_resource_handler)

#    url(r'^nodes/(\w+)/sensors/$', node_sensor_collection_handler),
#    url(r'^nodes/(\w+)/sensors/(\w+)$', node_sensor_resource_handler),
#    
#    url(r'^nodes/(\w+)/actuators/$', node_actuator_collection_handler),
#    url(r'^nodes/(\w+)/actuators/(\w+)$', node_actuator_resource_handler),

    
    # url(r'^nodegroups/$', nodegroup_collection_handler),
    # url(r'^nodegroups/(?P<nodegroup_id>\w+)$', nodegroup_resource_handler),
    
    # url(r'^nodegroups/(?P<nodegroup_id>\w+)/image/(?P<image_id>\w+)$', burn_image_to_nodegroup_handler),
    # url(r'^nodegroups/(?P<nodegroup_id>\w+)/image$', erase_image_to_nodegroup_handler),
    
    
    # url(r'^jobs/$', job_collection_handler),
    # url(r'^jobs/(?P<job_id>\w+)$', job_resource_handler),
  
    # url(r'^images/$', image_collection_handler),
    # url(r'^images/(?P<image_id>\w+)$', image_resource_handler),
    # url(r'^images/(?P<image_id>\w+)/upload$', imagefile_upload_handler),
    
    # url(r'^status/$', status_collection_handler),
    # url(r'^status/(?P<status_id>\w+)$', status_resource_handler),
    
)
