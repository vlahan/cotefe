from django.conf.urls.defaults import *
from testbedserver.api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', testbed_resource_handler),
                       
    url(r'^users/$', None), # GET
    url(r'^users/(?P<id>\w+)$', None), # GET
    
    url(r'^platforms/$', platform_collection_handler), # GET
    url(r'^platforms/(?P<platform_id>\w+)$', platform_resource_handler), # GET
    
    url(r'^nodes/$', node_collection_handler), # GET
    url(r'^nodes/(?P<node_id>\w+)$', node_resource_handler), # GET
    
    url(r'^nodegroups/(?P<nodegroup_id>\w+)/nodes/$', node_collection_in_nodegroup_handler), # GET
    url(r'^nodegroups/(?P<nodegroup_id>\w+)/nodes/(?P<node_id>\w+)$', node_resource_in_nodegroup_handler), # GET, PUT, DELETE
    
    url(r'^nodegroups/$', nodegroup_collection_handler), # GET, POST
    url(r'^nodegroups/(?P<nodegroup_id>\w+)$', nodegroup_resource_handler), # GET, PUT, DELETE
    
    url(r'^jobs/$', job_collection_handler), # GET, POST
    url(r'^jobs/(?P<job_id>\w+)$', job_resource_handler), # GET, PUT, DELETE
    
    url(r'^images/$', image_collection_handler), # GET, POST
    url(r'^images/(?P<image_id>\w+)$', image_resource_handler), # GET, PUT, DELETE
    
    url(r'^jobs/(?P<job_id>\w+)/traces/$', trace_collection_in_job_handler), # GET
    url(r'^jobs/(?P<job_id>\w+)/traces/(?P<trace_id>\w+)$', trace_resource_in_job_handler), # GET
    
    url(r'^jobs/(?P<job_id>\w+)/logs/$', log_collection_in_job_handler), # GET
    url(r'^jobs/(?P<job_id>\w+)/logs/(?P<log_id>\w+)$', log_resource_in_job_handler), # GET
    
    
)