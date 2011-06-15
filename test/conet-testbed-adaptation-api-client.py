import httplib2
import urlparse
import urllib
from anyjson import json

http = httplib2.Http()
f = file('image.json')
image = json.load(f)
print json.dumps(image, indent=4)