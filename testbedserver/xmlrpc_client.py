import xmlrpclib
from xmlrpclib import DateTime
from datetime import datetime
# import json

XMLRPC_HOST = '127.0.0.1'
XMLRPC_PORT = '8005'

# XMLRPC_HOST = 'www.twist.tu-berlin.de'
# XMLRPC_PORT = '8005'

XMLRPC_USERNAME = 'conetuser'
XMLRPC_PASSWORD = 'password'

proxy = xmlrpclib.ServerProxy('https://%s:%s@%s:%s/RPC2' % (XMLRPC_USERNAME, XMLRPC_PASSWORD, XMLRPC_HOST, XMLRPC_PORT))

try:
    print proxy.now()
    print proxy.getAllJobs()

except xmlrpclib.Fault, err:
    print "A fault occurred"
    print "Fault code: %d" % err.faultCode
    print "Fault string: %s" % err.faultString

except xmlrpclib.ProtocolError, err:
    print "A protocol error occurred"
    print "URL: %s" % err.url
    print "HTTP/HTTPS headers: %s" % err.headers
    print "Error code: %d" % err.errcode
    print "Error message: %s" % err.errmsg


# print s.now()
# print s.getAllPlatforms()
# print s.getAllJobs()

