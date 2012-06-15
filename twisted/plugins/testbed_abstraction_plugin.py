import os
import sys

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.web import server, resource, wsgi, static, client
from twisted.python import threadpool, util as tutil
from twisted.internet import reactor, defer, ssl
sys.path.append('/var/twist/twist_v1/conet/testbed_abstraction')

os.environ['DJANGO_SETTINGS_MODULE'] = 'testbed_abstraction.settings'
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler

class Options(usage.Options):
    optParameters = [["port", "p", 8001, "The port number to listen on."]]


class Root(resource.Resource):
    def __init__(self, wsgi_resource):
        resource.Resource.__init__(self)
        self.wsgi_resource = wsgi_resource

    def getChild(self, path, request):
        path0 = request.prepath.pop(0)
        request.postpath.insert(0, path0)
        return self.wsgi_resource

class ThreadPoolService(service.Service):
    def __init__(self, pool):
        self.pool = pool

    def startService(self):
        service.Service.startService(self)
        self.pool.start()

    def stopService(self):
        service.Service.stopService(self)
        self.pool.stop()



class ServerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = 'testbed_abstraction'
    description = 'Testbed Abstraction API Server'
    options = Options

    sslContext = ssl.DefaultOpenSSLContextFactory(
        tutil.sibpath(__file__, '../../../web2/cert/privkey.pem'),
        tutil.sibpath(__file__, '../../../web2/cert/cacert.pem')
        )
          
    def makeService(self, options):
        multi = service.MultiService()
        tps = ThreadPoolService(threadpool.ThreadPool())
        tps.setServiceParent(multi)
        resource = wsgi.WSGIResource(reactor, tps.pool, WSGIHandler())
        root = Root(resource)
#        static_resource = static.File(os.path.join(os.path.abspath('.'), 'mydjangosite/media'))
#        root.putChild('media', static_resource)
        site = server.Site(root)
        ws = internet.SSLServer(int(options["port"]), site, contextFactory=ServerServiceMaker.sslContext)
        ws.setServiceParent(multi)
        return multi

serviceMaker = ServerServiceMaker()
