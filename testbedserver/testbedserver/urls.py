from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

from api.admin import *
from api.views import *

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    
    url(r'^$', testbed_resource_handler),
    
    url(r'^platforms/$', platform_collection_handler),
        
    url(r'^nodes1/$', node_collection_handler),
    url(r'^nodes/4dd1ba50$', robot_resource_handler),
    url(r'^nodes/(?P<node_id>\w+)$', node_resource_handler),
    
    url(r'^nodegroups/$', nodegroup_collection_handler),
    url(r'^nodegroups/(?P<nodegroup_id>\w+)$', nodegroup_resource_handler),
    
    url(r'^nodegroups/(?P<nodegroup_id>\w+)/image/(?P<image_id>\w+)$', burn_image_to_nodegroup_handler),
    url(r'^nodegroups/(?P<nodegroup_id>\w+)/image$', erase_image_to_nodegroup_handler),
    
    
    url(r'^jobs/$', job_collection_handler),
    url(r'^jobs/(?P<job_id>\w+)$', job_resource_handler),
  
    url(r'^images/$', image_collection_handler),
    url(r'^images/(?P<image_id>\w+)$', image_resource_handler),
    url(r'^images/(?P<image_id>\w+)/upload$', imagefile_upload_handler),
    
    url(r'^status/$', status_collection_handler),
    url(r'^status/(?P<status_id>\w+)$', status_resource_handler),
)
