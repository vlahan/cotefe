from django.conf.urls.defaults import *
from api.views import *
from django.contrib import databrowse
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    # (r'^/$', testbed_resource_handler),
    (r'^jobs/$', job_collection_handler),
    # (r'^jobs/(?P<id>\d+)$', job_resource_handler),

    # (r'^admin/', include(admin.site.urls)),
    # (r'^databrowse/(.*)', databrowse.site.root),
    
    # (r'^api/', include('api.urls')),
)
