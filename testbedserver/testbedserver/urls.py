from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib import databrowse
from testbedserver.taa.views import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    
    # ADMIN URLS
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', include(admin.site.urls)),
    (r'^databrowse/(.*)', login_required(databrowse.site.root)),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^$', direct_to_template, { 'template': 'index.html' }, 'index'),
    (r'^api/', include('testbedserver.taa.urls')),
)
