from handlers import *

routes = [

    (r'^/init$', DatastoreInitialization),
    
    # (r'^/login$', Login),
    
    (r'^/openid/login$', OpenIDLogin),
    (r'^/openid/callback', OpenIDCallback),
    (r'^/openid/new', OpenIDNew),
    (r'^/openid/connect$', OpenIDConnect),
    
    (r'^/oauth2/auth$', OAuth2Authorize),
    (r'^/oauth2/token', OAuth2Token),
    
    (r'^/account$', Account),
    (r'^/identities', Identities),
    (r'^/sessions', Sessions),
    (r'^/docs$', Docs),
    (r'^/logout$', Logout),
    
    (r'^/me$', MeHandler),
    
    (r'^/users/$', UserCollectionHandler),
    (r'^/users/(\w*)$', UserResourceHandler),

    (r'^/$', FederationResourceHandler),
    
    (r'^/testbeds/$', TestbedCollectionHandler),
    (r'^/testbeds/(\w*)$', TestbedResourceHandler),
    
    (r'^/platforms/$', PlatformCollectionHandler),
    (r'^/platforms/(\w*)$', PlatformResourceHandler),
    
    (r'^/projects/$', ProjectCollectionHandler),
    (r'^/projects/(\w*)$', ProjectResourceHandler),
    
    
    # ('/tasks/', TasksHandler),
    # ('/tasks/456', TaskHandler),
    # ('/reflector', Reflector),
    
    
    # (r'^/testbeds/(.*)$', TestbedHandler),
    # (r'^/jobs/$', JobHandler),
    # (r'^/jobs/(.*)$', JobHandler),
    # (r'^/api/platforms/$', PlatformHandler),
    # (r'^/api/platforms/(.*)$', PlatformHandler),
    # (r'^/applications/$', ApplicationCollectionHandler),
    # (r'^/applications/(\w+)$', ApplicationResourceHandler),
    # 
    # (r'^/oauth2/auth', OAuth2AuthorizeHandler),
    # (r'^/oauth2/token', OAuth2AccessTokenHandler),

]