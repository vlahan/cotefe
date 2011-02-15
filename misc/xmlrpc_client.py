import xmlrpclib
from xmlrpclib import DateTime

host = '127.0.0.1'
port = '8001'

username = 'conetuser'
password = 'password'

s = xmlrpclib.ServerProxy('http://%s:%s@%s:%s/RPC2' % (username, password, host, port))
#s = xmlrpclib.ServerProxy("http://conetuser:password@127.0.0.1:8001/RPC2")

#print s.now()

#print s.now()
result = s.getAllJobs()

for item in result:
    for key in item:
        if isinstance(item[key], DateTime):
            item[key] = item[key].value

print result