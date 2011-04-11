from config import *
for f in Federation.all(): f.delete()

f1 = Federation()
f1.name = 'CONET Testbed Federation'
f1.put()

# INITIALIZE TESTBED DATASTORE
for t in Testbed.all(): t.delete()

t1 = Testbed()
t1.protocol = TS_PROTOCOL
t1.host = TS_HOST
t1.port = TS_PORT
t1.put()

# INITIALIZE JOB DATASTORE
for j in Job.all(): j.delete()


self.response.out.write('Datastore has been initialized!')