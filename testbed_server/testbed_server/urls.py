from django.conf.urls.defaults import *
from api.views import *
from django.contrib import admin
admin.autodiscover()
from django.contrib import databrowse

urlpatterns = patterns('',
#    (r'^users/$', user_collection_handler),
#    (r'^users/(?P<id>\d+)$', user_resource_handler),
    
    (r'^jobs/$', job_collection_handler),
    (r'^jobs/(?P<id>\d+)$', job_resource_handler),
    
    (r'^nodes/$', node_collection_handler),
    (r'^nodes/(?P<id>\d+)$', node_resource_handler),
    
    (r'^platforms/$', platform_collection_handler),
    (r'^platforms/(?P<id>\d+)$', platform_resource_handler),
    
    (r'^images/$', image_collection_handler),
    (r'^images/(?P<id>\d+)$', image_resource_handler),
    
    (r'^nodegroups/$', nodegroup_collection_handler),
    (r'^nodegroups/(?P<id>\d+)$', nodegroup_resource_handler),

    (r'^admin/', include(admin.site.urls)),
    (r'^databrowse/(.*)', databrowse.site.root),
    
    # (r'^api/', include('api.urls')),
)
