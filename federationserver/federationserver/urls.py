from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse
from api.admin import *

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('api.urls')),
)