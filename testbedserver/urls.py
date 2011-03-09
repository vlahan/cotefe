from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from testbedserver.taa.views import *
from django.contrib.auth.decorators import login_required

admin.autodiscover()

urlpatterns = patterns('',
    
    (r'^admin/doc/',         include('django.contrib.admindocs.urls')),
    (r'^admin/',             include(admin.site.urls)),
    (r'^databrowse/(.*)',    login_required(databrowse.site.root)),
    
    (r'^users/$',            user_collection_handler),
    
    (r'^$',                  testbed_resource_handler),
    (r'^platforms/$',        platform_collection_handler),
    (r'^platforms/(.*)$',    platform_resource_handler),
    (r'^jobs/$',             job_collection_handler),
    (r'^jobs/(.*)$',         job_resource_handler),
    
    (r'^api/', include('testbedserver.taa.urls')),
    
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^profiles/', include('profiles.urls')),
)
