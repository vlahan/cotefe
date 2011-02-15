from twistedserver import TwistedRPCServer
#s = TwistedRPCServer('user','pass')
s = TwistedRPCServer()

from twisted.web import server
from twisted.internet import reactor
reactor.listenTCP(8080, server.Site(s))
reactor.run()