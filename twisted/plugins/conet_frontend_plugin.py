import os
import sys

from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.internet import reactor, ssl
from twisted.plugin import IPlugin
from twisted.python import  usage, util as tutil
from twisted.web import server, resource, twcgi, static
from zope.interface import implements


class Options(usage.Options):
    optParameters = [["port", "p", 8002, "The port number to listen on."]]

class Root(resource.Resource):
    def __init__(self, twcgi_resource):
        resource.Resource.__init__(self)
        self.twcgi_resource = twcgi_resource

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.twcgi_resource

class PHPScript(twcgi.FilteredScript):
    filter = '/usr/bin/php-cgi'
    def runProcess(self, env, *a, **kw):
        env['REDIRECT_STATUS'] = '200'
        return twcgi.FilteredScript.runProcess(self, env, *a, **kw)

class ServerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'frontend'
    description = 'CONET Testbed Federation Frontend Server'
    options = Options

    sslContext = ssl.DefaultOpenSSLContextFactory(
        tutil.sibpath(__file__, 'cert/privkey.pem'),
        tutil.sibpath(__file__, 'cert/cacert.pem')
        )
          
    def makeService(self, options):
        application = service.Application('CONET Testbed Federation Frontend')
        sc = service.IServiceCollection(application)
        resource = static.File(os.path.join(os.path.abspath('.'), 'frontend'))
        resource.processors = {".php": PHPScript}
        resource.indexNames = ['index.php']
#        root = Root(resource)
        site = server.Site(resource)
        ws = internet.SSLServer(int(options["port"]), site, contextFactory=ServerServiceMaker.sslContext)
        ws.setServiceParent(sc)
        return sc

serviceMaker = ServerServiceMaker()
