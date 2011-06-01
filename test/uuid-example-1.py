# how to generate 32 hex digit random strings

import uuid, json

u = list()

for i in range(1000):
	x = uuid.uuid4().hex
	if len(u) == 0:
		u.append(x)
	else:	
		if x in u:
			print "trovato!"
		else:
			u.append(x)

print json.dumps(u, indent = 4)