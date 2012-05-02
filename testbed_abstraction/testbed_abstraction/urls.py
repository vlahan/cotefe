from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from api.views import root_handler, collection_handler, resource_handler

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'', include('testbed_abstraction.api.urls')),
    
    url(r'^$', root_handler),
                       
    url(r'^(\w+)/$', collection_handler),
    url(r'^(\w+)/(\w+)$', resource_handler),
    
)
