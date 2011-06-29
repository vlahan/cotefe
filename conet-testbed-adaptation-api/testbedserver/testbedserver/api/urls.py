from django.conf.urls.defaults import *
from testbedserver.api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', testbed_resource_handler),
                       
#    url(r'^users/$', None),
#    url(r'^users/(?P<id>\w+)$', None),
    
    url(r'^platforms/$', platform_collection_handler),
    url(r'^platforms/(?P<platform_uid>\w+)$', platform_resource_handler),
    
    url(r'^nodes/$', node_collection_handler),
    url(r'^nodes/(?P<node_uid>\w+)$', node_resource_handler),
    
    url(r'^nodes/(?P<node_uid>\w+)/image/(?P<image_uid>\w+)$', image_resource_in_node_handler),
    
    url(r'^nodegroups/$', nodegroup_collection_handler),
    url(r'^nodegroups/(?P<nodegroup_uid>\w+)$', nodegroup_resource_handler),
    
    url(r'^nodegroups/(?P<nodegroup_uid>\w+)/nodes/$', node_collection_in_nodegroup_handler),
    url(r'^nodegroups/(?P<nodegroup_uid>\w+)/nodes/(?P<node_uid>\w+)$', node_resource_in_nodegroup_handler),
    
    url(r'^nodegroups/(?P<nodegroup_uid>\w+)/image/(?P<image_uid>\w+)$', image_resource_in_nodegroup_handler),
    
    
    url(r'^jobs/$', job_collection_handler),
    url(r'^jobs/(?P<job_uid>\w+)$', job_resource_handler),
  
    url(r'^images/$', image_collection_handler),
    url(r'^images/(?P<image_uid>\w+)$', image_resource_handler),

#    url(r'^jobs/(?P<job_uid>\w+)/traces/$', trace_collection_in_job_handler),
#    url(r'^jobs/(?P<job_uid>\w+)/traces/(?P<trace_uid>\w+)$', trace_resource_in_job_handler),
#    
#    url(r'^jobs/(?P<job_uid>\w+)/logs/$', log_collection_in_job_handler),
#    url(r'^jobs/(?P<job_uid>\w+)/logs/(?P<log_uid>\w+)$', log_resource_in_job_handler),
    
    
)