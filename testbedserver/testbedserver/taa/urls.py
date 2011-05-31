from django.conf.urls.defaults import *
from testbedserver.taa.views import *

urlpatterns = patterns('',

    # TAA URLS
    (r'^$', testbed_resource_handler),
    
    (r'^users/$', user_collection_handler),
    (r'^users/(.*)$', user_resource_handler),
    
    (r'^platforms/$', platform_collection_handler),
    (r'^platforms/(.*)$', platform_resource_handler),
    
    (r'^jobs/$', job_collection_handler),
    (r'^jobs/(.*)$', job_resource_handler),

)
