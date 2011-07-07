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
    url(r'^projects/(?P<project_id>\w+)/experiments/$', experiment_collection_in_project_handler),
    
    url(r'^experiments/$', experiment_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)$', experiment_resource_handler),
    
    url(r'^property-sets/$', property_set_collection_handler),
    url(r'^property-sets/(?P<property_set_id>\w+)$', property_set_resource_handler),
)