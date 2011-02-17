import xmlrpclib
from xmlrpclib import DateTime
from datetime import datetime
import json

host = '127.0.0.1'
port = '8002'

username = 'conetuser'
password = 'password'

s = xmlrpclib.ServerProxy('http://%s:%s@%s:%s/RPC2' % (username, password, host, port))

#print s.now()

#result = s.getAllJobs()
#
#for item in result:
#    for key in item:
#        if isinstance(item[key], DateTime):
#            # http://en.wikipedia.org/wiki/ISO_8601
#            item[key] = datetime.strptime(item[key].value, "%Y%m%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+01:00")     
#
#print json.dumps(result, indent=4)

print s.getAllPlatforms()