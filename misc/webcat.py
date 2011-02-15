from twisted.web import client
from twisted.internet import reactor

def printPage(data):
    print data
    reactor.stop()
    
def printError(failure):
    print >> sys.stderr, "Error:", failure.getErrorMessage()
    reactor.stop()
    
url = "http://www.google.com"

client.getPage(url).addCallback(printPage).addErrback(printError)
reactor.run()
