import xmlrpclib
from xmlrpclib import DateTime
from datetime import datetime
import json

XMLRPC_HOST = '127.0.0.1'
XMLRPC_PORT = '8002'

USERNAME = 'conetuser'
PASSWORD = 'password'

s = xmlrpclib.ServerProxy('http://%s:%s@%s:%s/RPC2' % (USERNAME, PASSWORD, XMLRPC_HOST, XMLRPC_PORT))

print s.getAllPlatforms()
print s.getAllJobs()

