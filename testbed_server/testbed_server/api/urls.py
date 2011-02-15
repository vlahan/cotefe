from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import *

testbed_handler = Resource(TestbedHandler)
job_handler = Resource(JobHandler)
task_handler = Resource(TaskHandler)
trace_handler = Resource(TraceHandler)
log_handler = Resource(LogHandler)
imageformat_handler = Resource(ImageHandler)
image_handler = Resource(ImageFormatHandler)
platform_handler = Resource(PlatformHandler)
interface_handler = Resource(InterfaceHandler)
radio_handler = Resource(RadioHandler)
sensor_handler = Resource(SensorHandler)
actuator_handler = Resource(ActuatorHandler)
mobility_handler = Resource(MobilityHandler)
node_handler = Resource(NodeHandler)
nodegroup_handler = Resource(NodeGroupHandler)
socket_handler = Resource(SocketHandler)

urlpatterns = patterns('',
    url(r'^testbeds/', testbed_handler),
    url(r'^jobs/', job_handler),
    url(r'^tasks/', task_handler),
    url(r'^traces/', trace_handler),
    url(r'^logs/', log_handler),
    url(r'^imageformats/', imageformat_handler),
    url(r'^images/', image_handler),
    url(r'^platforms/', platform_handler),
    url(r'^interfaces', interface_handler),
    url(r'^radios/', radio_handler),
    url(r'^sensors/', sensor_handler),
    url(r'^actuators/', actuator_handler),
    url(r'^mobilitys/', mobility_handler),
    url(r'^nodes/', node_handler),
    url(r'^platforms/', platform_handler),
    url(r'^nodegroups/', nodegroup_handler),
    url(r'^sockets/', socket_handler),
)
