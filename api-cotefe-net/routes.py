from handlers import *

routes = [    

    ## ADMIN ONLY #
    
    (r'^/admin/init$', DatastoreInitialization),
    
    # (r'^/login$', Login),
    
    ## OPENID HANDLERS ##
    
    (r'^/openid/login$', OpenIDLogin),
    (r'^/openid/callback', OpenIDCallback),
    (r'^/openid/new', OpenIDNew),
    (r'^/openid/connect$', OpenIDConnect),
    
    ## OAUTH2 HANDLERS ##
    
    (r'^/oauth2/auth$', OAuth2Authorize),
    (r'^/oauth2/token', OAuth2Token),
    
    ## COTEFE IDENTITY/SESSIONS/APPS MANAGEMENT INTERFACE ##
    
    (r'^/account$', Account),
    (r'^/identities', Identities),
    (r'^/sessions', Sessions),
    (r'^/applications', Applications),
    (r'^/logout$', Logout),
    
    ## COTEFE API ##
    
    (r'^/$', FederationResourceHandler),
    
    (r'^/me$', MeHandler),
    (r'^/me/images/$', MeHandler),
    (r'^/me/experiments/$', MeHandler),
    (r'^/me/jobs/$', MeHandler),
    
    (r'^/users/$', UserCollectionHandler),
    (r'^/users/(\d+)$', UserResourceHandler),
    # (r'^/users/(\d+)/images/$', UserImageCollectionHandler),
    # (r'^/users/(\d+)/experiments/$', UserExperimentCollectionHandler),
    # (r'^/users/(\d+)/jobs/$', UserJobCollectionHandler),
    
    (r'^/platforms/$', PlatformCollectionHandler),
    (r'^/platforms/(\w+)$', PlatformResourceHandler),
    
    (r'^/interfaces/$', InterfaceCollectionHandler),
    (r'^/interfaces/(\w+)$', InterfaceResourceHandler),
    
    (r'^/sensors/$', SensorCollectionHandler),
    (r'^/sensors/(\w+)$', SensorResourceHandler),
    
    (r'^/actuators/$', ActuatorCollectionHandler),
    (r'^/actuators/(\w+)$', ActuatorResourceHandler),
    
    (r'^/testbeds/$', TestbedCollectionHandler),
    (r'^/testbeds/(\d+)$', TestbedResourceHandler),
    
    # IMAGE
    
    (r'^/images/$', ImageCollectionHandler),
    (r'^/images/(\d+)$', ImageResourceHandler),
    (r'^/images/(\d+)/upload$', ImageUploadHandler),
    (r'^/images/(\d+)/download$', ImageDownloadHandler),
    
    # PROJECT
    
    (r'^/projects/$', ProjectCollectionHandler),
    (r'^/projects/(\d+)$', ProjectResourceHandler),
    
    # EXPERIMENT
    
    (r'^/experiments/$', ExperimentCollectionHandler),
    (r'^/experiments/(\d+)$', ExperimentResourceHandler),
    
    (r'^/experiments/(\d+)/property-sets/$', PropertySetCollectionHandler),
    (r'^/experiments/(\d+)/property-sets/(\d+)$', PropertySetResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodes/$', VirtualNodeCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodes/(\d+)$', VirtualNodeResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodegroups/$', VirtualNodeGroupCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodegroups/(\d+)$', VirtualNodeGroupResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-tasks/$', VirtualTaskCollectionHandler),
    (r'^/experiments/(\d+)/virtual-tasks/(\d+)$', VirtualTaskResourceHandler),
    
    # JOB
    
    (r'^/jobs/$', JobCollectionHandler),
    (r'^/jobs/(\d+)$', JobResourceHandler),

    # (r'^/jobs/(\d+)/nodes/$', NodeCollectionHandler),
    # (r'^/jobs/(\d+)/nodes/(\d+)$', NodeResourceHandler),
    
    # (r'^/jobs/(\d+)/nodegroups/$', NodeGroupCollectionHandler),
    # (r'^/jobs/(\d+)/nodegroups/(\d+)$', NodeGroupResourceHandler),
    
    # (r'^/jobs/(\d+)/tasks/$', TaskCollectionHandler),
    # (r'^/jobs/(\d+)/tasks/(\d+)$', TaskResourceHandler),
    
    # (r'^/jobs/(\d+)/logs/$', LogsCollectionHandler),
    # (r'^/jobs/(\d+)/logs/(\d+)$', LogResourceHandler),
    
    # (r'^/jobs/(\d+)/traces/$', TraceCollectionHandler),
    # (r'^/jobs/(\d+)/traces/(\d+)$', TraceResourceHandler),

]