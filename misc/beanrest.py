from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import beanstalkc
import json
import yaml

class BeanstalkdTube(Resource):
    isLeaf = True
    def __init__(self, beanstalk, tube, pass_headers):
        Resource.__init__(self)
        self.beanstalk = beanstalk
        self.tube = tube
        self.passHeaders = pass_headers

    def render_GET(self, request):
        try:
            return json.dumps(self.beanstalk.stats_tube(self.tube), sort_keys=True, indent=4)
        except beanstalkc.CommandFailed:
            request.setResponseCode(404)
            return 'Invalid or empty tube.'

    def render_POST(self, request):
        self.beanstalk.use(self.tube)
        job = request.content.getvalue()

        # If we should pass through headers and the incoming request is JSON,
        # add the header dictionary to the incoming request.
        if self.passHeaders and request.getHeader('Content-Type') == 'application/json':
            decoded_job = json.loads(job)
            decoded_job['headers'] = request.getAllHeaders()
            job = json.dumps(decoded_job)

        id = self.beanstalk.put(job)
        # TODO: Set an absolute URL per the RFC for the Location header.
        request.setHeader('Location', '/%s/%d' % (self.tube, id))
        request.setResponseCode(201)
        return "Inserted item %d into tube %s.\n" % (id, self.tube)

class BeanstalkdStats(Resource):
    def __init__(self, beanstalk):
        Resource.__init__(self)
        self.beanstalk = beanstalk

    def render_GET(self, request):
        return json.dumps(self.beanstalk.stats(), sort_keys=True, indent=4)

class Beanstalkd(Resource):
  def __init__(self, pass_headers):
      Resource.__init__(self)
      self.beanstalk = beanstalkc.Connection()
      self.passHeaders = pass_headers

  def getChild(self, name, request):
      request.setHeader('Content-Type', 'application/json')
      if name == '':
          return BeanstalkdStats(self.beanstalk)
      return BeanstalkdTube(self.beanstalk, name, self.passHeaders)

file = open ('config.yaml')
configuration = yaml.load(file.read())
file.close()
root = Beanstalkd(configuration['pass_headers'])
factory = Site(root)
reactor.listenTCP(configuration['port'], factory, interface=configuration['interface'])
reactor.run()
