from handlers import *

routes = [    

    (r'^/admin/init$', DatastoreInitialization),
    
    (r'^/login$', Login),
    
    (r'^/openid/login$', OpenIDLogin),
    (r'^/openid/callback', OpenIDCallback),
    (r'^/openid/new', OpenIDNew),
    (r'^/openid/connect$', OpenIDConnect),
    
    (r'^/oauth2/auth$', OAuth2Authorize),
    (r'^/oauth2/token', OAuth2Token),
    
    (r'^/account$', Account),
    (r'^/identities', Identities),
    (r'^/sessions', Sessions),
    (r'^/applications', Applications),
    (r'^/logout$', Logout),
    
    (r'^/me$', MeHandler),
    
    (r'^/users/$', UserCollectionHandler),
    (r'^/users/(\d+)$', UserResourceHandler),

    (r'^/$', FederationResourceHandler),
    
    (r'^/testbeds/$', TestbedCollectionHandler),
    (r'^/testbeds/(\d+)$', TestbedResourceHandler),
    
    (r'^/platforms/$', PlatformCollectionHandler),
    (r'^/platforms/(\w+)$', PlatformResourceHandler),
    
#    (r'^/interfaces/$', InterfaceCollectionHandler),
#    (r'^/interfaces/(\w+)$', InterfaceResourceHandler),
#    
#    (r'^/sensors/$', SensorCollectionHandler),
#    (r'^/sensors/(\w+)$', SensorResourceHandler),
#    
#    (r'^/actuators/$', ActuatorCollectionHandler),
#    (r'^/actuators/(\w+)$', ActuatorResourceHandler),
    
    (r'^/projects/$', ProjectCollectionHandler),
    (r'^/projects/(\d+)$', ProjectResourceHandler),
    
    (r'^/experiments/$', ExperimentCollectionHandler),
    (r'^/experiments/(\d+)$', ExperimentResourceHandler),
    
    (r'^/experiments/(\d+)/images/$', ImageCollectionHandler),
    (r'^/experiments/(\d+)/images/(\d+)$', ImageResourceHandler),
    (r'^/experiments/(\d+)/images/(\d+)/upload$', ImageUploadHandler),
    (r'^/experiments/(\d+)/images/(\d+)/download$', ImageDownloadHandler),
    
    (r'^/experiments/(\d+)/property-sets/$', PropertySetCollectionHandler),
    (r'^/experiments/(\d+)/property-sets/(\d+)$', PropertySetResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodes/$', VirtualNodeCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodes/(\d+)$', VirtualNodeResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodegroups/$', VirtualNodeGroupCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodegroups/(\d+)$', VirtualNodeGroupResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-tasks/$', VirtualTaskCollectionHandler),
    (r'^/experiments/(\d+)/virtual-tasks/(\d+)$', VirtualTaskResourceHandler),
    
    (r'^/experiments/(\d+)/jobs/$', VirtualTaskCollectionHandler),
    (r'^/experiments/(\d+)/jobs/(\d+)$', VirtualTaskResourceHandler),

]