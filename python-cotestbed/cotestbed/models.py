from cotestbed import utils

class Resource(object):
    
    def __repr__(self):
        return self.uri
    
    def __str__(self):
        return self.__repr__()
    
    def __unicode__(self):
        return self.__repr__()

class Testbed(Resource):
    
    def __init__(self, d):
        self.uri = d['uri']
        self.name = d['name']
        self.organization = d['organization']
        
class Node(Resource):
    def __init__(self, d):
        self.uri = d['uri']
        self.id = d['id']
        self.name = d['name']
        self.platform = d['platform']['id']
        
class Job(Resource):
    def __init__(self, d, nodes):
        self.uri = d['uri']
        self.id = d['id']
        self.name = d['name']
        self.description = d['description']
        self.datetime_from = utils.string_to_utc_datetime(d['datetime_from'])
        self.datetime_to = utils.string_to_utc_datetime(d['datetime_to'])
        self.nodes = nodes
 
class Image(Resource):
    def __init__(self, d, job):
        self.uri = d['uri']
        self.id = d['id']
        self.name = d['name']
        self.description = d['description']
        self.job = job

class NodeGroup(Resource):
    def __init__(self, d, job, nodes):
        self.uri = d['uri']
        self.id = d['id']
        self.name = d['name']
        self.description = d['description']
        self.job = job
        self.nodes = nodes

#class Task(Resource):
#    def __init__(self, d, job):
#        self.uri = d['uri']
#        self.id = d['id']
#        self.name = d['name']
#        self.description = d['description']
#        action = {
#            'PUT': 'install',
#            'DELETE': 'erase'
#        }
#        self.action = action[d['method']]
#        self.target = d['target']
#        self.job = job
        
class Status(Resource):
    def __init__(self, d):
        self.uri = d['uri']
        self.id = d['id']
        self.http_request = d['http_request']
        self.status = d['status']