class Resource(object):
    
    def __repr__(self):
        return self.uri
    
    def __str__(self):
        return self.__repr__()
    
    def __unicode__(self):
        return self.__repr__()
    
class User(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.username = d['username']
        self.first = d['first']
        self.last = d['last']
        self.email = d['email']
        self.organization = d['organization']

class Federation(Resource):
    def __init__(self, d):
        self.uri = d['uri']
        self.name = d['name']

class Testbed(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.organization = d['organization']

class Platform(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Project(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        
class Experiment(Resource):
    def __init__(self, d, project):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        self.project = project
        
class Image(Resource):
    def __init__(self, d, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        self.experiment = experiment

class PropertySet(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        self.platform = platform
        self.experiment = experiment

class VirtualNode(Resource):
    def __init__(self, d, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.experiment = experiment

class VirtualNodeGroup(Resource):
    def __init__(self, d, virtual_nodes, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        self.virtual_nodes = virtual_nodes
        self.experiment = experiment

class VirtualTask(Resource):
    
    def __init__(self, d, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        action = {
            'PUT': 'install',
            'DELETE': 'erase'
        }
        self.action = action[d['method']]
        self.target = d['target']
        self.experiment = experiment

class Job(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Node(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class NodeGroup(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Task(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Trace(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Log(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']

class Status(Resource):
    def __init__(self, d, platform, experiment):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']