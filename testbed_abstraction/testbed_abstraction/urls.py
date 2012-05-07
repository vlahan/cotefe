from django.conf.urls import patterns, include, url

from api.views import root_handler, collection_handler, resource_handler

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', root_handler),
                       
    url(r'^(\w+)/$', collection_handler),
    url(r'^(\w+)/(\w+)$', resource_handler),
    
)
