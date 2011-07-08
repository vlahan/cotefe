from django.conf.urls.defaults import *
from federationserver.api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', federation_resource_handler),
    
    url(r'^testbeds/$', testbed_collection_handler),
    url(r'^testbeds/(?P<testbed_id>\w+)$', testbed_resource_handler),
    
    url(r'^platforms/$', platform_collection_handler),
    url(r'^platforms/(?P<platform_id>\w+)$', platform_resource_handler),
                       
    url(r'^projects/$', project_collection_handler),
    url(r'^projects/(?P<project_id>\w+)$', project_resource_handler),
    
    url(r'^experiments/$', experiment_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)$', experiment_resource_handler),
    
    url(r'^property-sets/$', property_set_collection_handler),
    url(r'^property-sets/(?P<property_set_id>\w+)$', property_set_resource_handler),
    
    url(r'^virtual-nodes/$', virtual_node_collection_handler),
    url(r'^virtual-nodes/(?P<virtual_node_id>\w+)$', virtual_node_resource_handler),
    
    url(r'^virtual-nodegroups/$', virtual_nodegroup_collection_handler),
    url(r'^virtual-nodegroups/(?P<virtual_nodegroup_id>\w+)$', virtual_nodegroup_resource_handler),
    
)