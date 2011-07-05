from django.conf.urls.defaults import *
from api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', federation_resource_handler),
                       
    url(r'^projects/$', project_collection_handler),
    url(r'^projects/(?P<project_uid>\w+)$', project_resource_handler),
    url(r'^projects/(?P<project_uid>\w+)/experiments/$', experiment_collection_in_project_handler),
    
    url(r'^experiments/$', experiment_collection_handler),
    url(r'^experiments/(?P<experiment_uid>\w+)$', experiment_resource_handler),
)