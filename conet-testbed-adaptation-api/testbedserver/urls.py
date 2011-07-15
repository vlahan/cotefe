from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib import databrowse

try:
    from api.admin import *
    from api.views import *
except ImportError:
    from testbedserver.api.admin import *
    from testbedserver.api.views import *

# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('testbedserver.api.urls')),
    url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
)