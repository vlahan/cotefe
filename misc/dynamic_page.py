from twisted.internet import reactor
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
import time

class ClockPage(Resource):
    isLeaf = True
    def render_GET(self, request):
        # return "<html><body>%s</body></html>" % (time.ctime(),)
        return NOT_DONE_YET

resource = ClockPage()
factory = Site(resource)
reactor.listenTCP(8880, factory)
reactor.run()