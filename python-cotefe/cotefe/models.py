class Resource(object):
    pass
    
class User(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.username = d['username']
        self.first = d['first']
        self.last = d['last']
        self.email = d['email']
        self.organization = d['organization']
        
    def __str__(self):
        return '%s %s' % (self.first, self.last)

class Federation(Resource):
    def __init__(self, d):
        self.uri = d['uri']
        self.name = d['name']

class Testbed(Resource):
    pass

class Platform(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        
    def __str__(self):
        return self.name

class Project(Resource):
    def __init__(self, d):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
    
    def __str__(self):
        return self.name
        
class Experiment(Resource):
    def __init__(self, d, project):
        self.id = d['id']
        self.uri = d['uri']
        self.name = d['name']
        self.description = d['description']
        self.project = project
    
    def __str__(self):
        return self.name

class PropertySet(Resource):
    pass

class VirtualNode(Resource):
    pass

class VirtualNodeGroup(Resource):
    pass

class VirtualTask(Resource):
    pass

class Image(Resource):
    pass

class Job(Resource):
    pass

class Node(Resource):
    pass

class NodeGroup(Resource):
    pass

class Task(Resource):
    pass

class Trace(Resource):
    pass

class Log(Resource):
    pass

class Status(Resource):
    pass