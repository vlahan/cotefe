from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

from testbedserver.api.admin import *
from testbedserver.api.databrowse import *
from testbedserver.api.views import *

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^databrowse/(.*)', databrowse.site.root),
    url(r'', include('testbedserver.api.urls')),
)