from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import *

testbed_handler = Resource(TestbedHandler)
job_handler = Resource(JobHandler)

urlpatterns = patterns('',
    url(r'^testbeds/', testbed_handler),
    url(r'^jobs/', job_handler),
)
