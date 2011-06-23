from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse
from federationserver.api.admin import *
from federationserver.api.databrowse import *
from federationserver.api.views import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template


# admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^databrowse/(.*)', databrowse.site.root),
    # url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'', include('federationserver.api.urls')),
)