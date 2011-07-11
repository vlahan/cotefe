from django.conf.urls.defaults import *
from testbedserver.api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', testbed_resource_handler),
    
    url(r'^platforms/$', platform_collection_handler),
        
    url(r'^nodes/$', node_collection_handler),
    url(r'^nodes/(?P<node_id>\w+)$', node_resource_handler),
    
    url(r'^nodes/(?P<node_id>\w+)/image/(?P<image_id>\w+)$', image_resource_in_node_handler),
    
    url(r'^nodegroups/$', nodegroup_collection_handler),
    url(r'^nodegroups/(?P<nodegroup_id>\w+)$', nodegroup_resource_handler),
    
    url(r'^nodegroups/(?P<nodegroup_id>\w+)/image/(?P<image_id>\w+)$', image_resource_in_nodegroup_handler),
    
    
    url(r'^jobs/$', job_collection_handler),
    url(r'^jobs/(?P<job_id>\w+)$', job_resource_handler),
  
    url(r'^images/$', image_collection_handler),
    url(r'^images/(?P<image_id>\w+)$', image_resource_handler),
    
    url(r'^images/(?P<image_id>\w+)/upload$', imagefile_upload_handler),

#    url(r'^jobs/(?P<job_id>\w+)/traces/$', trace_collection_in_job_handler),
#    url(r'^jobs/(?P<job_id>\w+)/traces/(?P<trace_id>\w+)$', trace_resource_in_job_handler),
#    
#    url(r'^jobs/(?P<job_id>\w+)/logs/$', log_collection_in_job_handler),
#    url(r'^jobs/(?P<job_id>\w+)/logs/(?P<log_id>\w+)$', log_resource_in_job_handler),
    
    
)