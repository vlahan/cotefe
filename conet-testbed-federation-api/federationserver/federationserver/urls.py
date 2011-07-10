from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

try:
    from federationserver.api.admin import *
    from federationserver.api.databrowse import *  
except ImportError:
    from api.admin import *
    from api.databrowse import *

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^databrowse/(.*)', databrowse.site.root),
    url(r'', include('api.urls')),
)