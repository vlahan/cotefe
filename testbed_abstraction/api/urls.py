from django.conf.urls import patterns, url


from api.views import root_handler, collection_handler, resource_handler

urlpatterns = patterns('',
    
    url(r'^$', root_handler),
                       
    url(r'^(\w+)/$', collection_handler),
    url(r'^(\w+)/(\w+)$', resource_handler),
    
)