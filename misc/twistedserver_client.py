from xmlrpclib import ServerProxy

#p = ServerProxy('http://localhost:8080')
#p.echo('hi')

p = ServerProxy('http://user:pass@localhost:8080')
print   p.echo('hi')
