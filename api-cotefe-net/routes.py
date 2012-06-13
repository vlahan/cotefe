from handlers import admin, openid, oauth2, www, user, federation, platform, interface, sensor, actuator, testbed, image, project, experiment, propertyset, virtualnode, virtualnodegroup, virtualtask, job

routes = [    

    ## ADMIN ONLY #
    
    (r'^/admin/init$', admin.DatastoreInitialization),
    
    ## OPENID HANDLERS ##
    
    (r'^/openid/login$', openid.OpenIDLogin),
    (r'^/openid/callback', openid.OpenIDCallback),
    (r'^/openid/new', openid.OpenIDNew),
    (r'^/openid/connect$', openid.OpenIDConnect),
    
    ## OAUTH2 HANDLERS ##
    
    (r'^/oauth2/auth$', oauth2.OAuth2Authorize),
    (r'^/oauth2/token', oauth2.OAuth2Token),
    
    ## COTEFE IDENTITY/SESSIONS/APPS MANAGEMENT INTERFACE ##
    
    (r'^/login$', www.Login),
    (r'^/account$', www.Account),
    (r'^/identities', www.Identities),
    (r'^/sessions', www.Sessions),
    (r'^/applications', www.Applications),
    (r'^/logout$', www.Logout),
    
    ## COTEFE API ##
    
    (r'^/$', federation.FederationResourceHandler),
    
    (r'^/me$', user.MeHandler),
    # (r'^/me/images/$', user.MyImages),
    # (r'^/me/projects/$', user.MyProjects),
    # (r'^/me/experiments/$', user.MyExperiments),
    # (r'^/me/jobs/$', user.MyJobs),
    
    (r'^/users/$', user.UserCollectionHandler),
    (r'^/users/(\d+)$', user.UserResourceHandler),
    # (r'^/users/(\d+)/images/$', user.UserImageCollectionHandler),
    # (r'^/users/(\d+)/experiments/$', user.UserExperimentCollectionHandler),
    # (r'^/users/(\d+)/jobs/$', user.UserJobCollectionHandler),
    
    (r'^/platforms/$', platform.PlatformCollectionHandler),
    (r'^/platforms/(\w+)$', platform.PlatformResourceHandler),
    
    (r'^/interfaces/$', interface.InterfaceCollectionHandler),
    (r'^/interfaces/(\w+)$', interface.InterfaceResourceHandler),
    
    (r'^/sensors/$', sensor.SensorCollectionHandler),
    (r'^/sensors/(\w+)$', sensor.SensorResourceHandler),
    
    (r'^/actuators/$', actuator.ActuatorCollectionHandler),
    (r'^/actuators/(\w+)$', actuator.ActuatorResourceHandler),
    
    (r'^/testbeds/$', testbed.TestbedCollectionHandler),
    (r'^/testbeds/(\w+)$', testbed.TestbedResourceHandler),
    
    # IMAGE
    
    (r'^/images/$', image.ImageCollectionHandler),
    (r'^/images/(\d+)$', image.ImageResourceHandler),
    (r'^/images/(\d+)/upload$', image.ImageUploadHandler),
    (r'^/images/(\d+)/download$', image.ImageDownloadHandler),
    
    (r'^/image-upload-form$', image.ImageUploadForm),
    
    # PROJECT
    
    (r'^/projects/$', project.ProjectCollectionHandler),
    (r'^/projects/(\d+)$', project.ProjectResourceHandler),
    
    # EXPERIMENT
    
    (r'^/experiments/$', experiment.ExperimentCollectionHandler),
    (r'^/experiments/(\d+)$', experiment.ExperimentResourceHandler),
    
    (r'^/experiments/(\d+)/property-sets/$', propertyset.PropertySetCollectionHandler),
    (r'^/experiments/(\d+)/property-sets/(\d+)$', propertyset.PropertySetResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodes/$', virtualnode.VirtualNodeCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodes/(\d+)$', virtualnode.VirtualNodeResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-nodegroups/$', virtualnodegroup.VirtualNodeGroupCollectionHandler),
    (r'^/experiments/(\d+)/virtual-nodegroups/(\d+)$', virtualnodegroup.VirtualNodeGroupResourceHandler),
    
    (r'^/experiments/(\d+)/virtual-tasks/$', virtualtask.VirtualTaskCollectionHandler),
    (r'^/experiments/(\d+)/virtual-tasks/(\d+)$', virtualtask.VirtualTaskResourceHandler),
    
    # JOB
    
    (r'^/jobs/$', job.JobCollectionHandler),
    (r'^/jobs/(\d+)$', job.JobResourceHandler),

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