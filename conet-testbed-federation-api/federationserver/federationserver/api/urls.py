from django.conf.urls.defaults import *
from federationserver.api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', federation_resource_handler),
                       
    url(r'^projects/$', project_collection_handler), # GET
    url(r'^projects/(?P<project_id>\w+)$', project_resource_handler), # GET
    
    url(r'^experiments/$', experiment_collection_handler), # GET
    url(r'^experiments/(?P<experiment_id>\w+)$', experiment_resource_handler), # GET
)