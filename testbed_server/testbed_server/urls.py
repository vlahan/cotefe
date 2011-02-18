from django.conf.urls.defaults import *
from api.views import *
from django.contrib import databrowse
from django.contrib import admin
admin.autodiscover()
import registration

urlpatterns = patterns('',
    
    (r'^admin/',             include('admin.site.urls')),
    (r'^databrowse/(.*)',    databrowse.site.root),
    
    (r'^users/$',            user_collection_handler),
    
    (r'^$',                  testbed_resource_handler),
    (r'^platforms/$',        platform_collection_handler),
    (r'^platforms/(.*)$',    platform_resource_handler),
    (r'^jobs/$',             job_collection_handler),
    (r'^jobs/(.*)$',         job_resource_handler),
    
    # (r'^api/', include('api.urls')),
)
