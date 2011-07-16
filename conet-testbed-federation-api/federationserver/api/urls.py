from django.conf.urls.defaults import *
from api.views import *

urlpatterns = patterns('',
                       
    url(r'^$', federation_resource_handler),
    
    url(r'^testbeds/$', testbed_collection_handler),
    url(r'^testbeds/(?P<testbed_id>\w+)$', testbed_resource_handler),
    
    url(r'^platforms/$', platform_collection_handler),
    url(r'^platforms/(?P<platform_id>\w+)$', platform_resource_handler),
    
    url(r'^projects/$', project_collection_handler),
    url(r'^projects/(?P<project_id>\w+)$', project_resource_handler),
    
    url(r'^experiments/$', experiment_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)$', experiment_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/property-sets/$', property_set_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/property-sets/(?P<property_set_id>\w+)$', property_set_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodes/$', virtual_node_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodes/(?P<virtual_node_id>\w+)$', virtual_node_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodegroups/$', virtual_nodegroup_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodegroups/(?P<virtual_nodegroup_id>\w+)$', virtual_nodegroup_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-tasks/$', virtual_task_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-tasks/(?P<virtual_task_id>\w+)$', virtual_task_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/images/$', image_collection_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/images/(?P<image_id>\w+)$', image_resource_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/images/(?P<image_id>\w+)/upload$', imagefile_upload_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/images/(?P<image_id>\w+)/download$', imagefile_download_handler),
    
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodes/(?P<virtual_node_id>\w+)/image/(?P<image_id>\w+)$', image_resource_in_virtual_node_handler),
    url(r'^experiments/(?P<experiment_id>\w+)/virtual-nodegroups/(?P<virtual_nodegroup_id>\w+)/image/(?P<image_id>\w+)$', image_resource_in_virtual_nodegroup_handler),
    
    url(r'^jobs/$', job_collection_handler),
    url(r'^jobs/(?P<job_id>\w+)$', job_resource_handler),
    
    url(r'^jobs/(?P<job_id>\w+)/tasks/$', task_collection_handler),
    url(r'^jobs/(?P<job_id>\w+)/tasks/(?P<task_id>\w+)$', task_resource_handler),
    
    
)