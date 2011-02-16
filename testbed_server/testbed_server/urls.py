from django.conf.urls.defaults import patterns, include
from api.views import job_collection_handler, job_resource_handler, testbed_resource_handler
from django.contrib import admin
admin.autodiscover()
from django.contrib import databrowse

urlpatterns = patterns('',
    
    (r'^/$', testbed_resource_handler),
    (r'^jobs/$', job_collection_handler),
    (r'^jobs/(?P<id>\d+)$', job_resource_handler),

    (r'^admin/', include(admin.site.urls)),
    (r'^databrowse/(.*)', databrowse.site.root),
    
    # (r'^api/', include('api.urls')),
)
