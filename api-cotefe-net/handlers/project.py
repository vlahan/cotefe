import utils

from models import Project
from handlers import OAuth2RESTJSONHandler

class ProjectCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        project_list = list()
        
        try:
            query = Project.all().filter('owner =', self.user)
        except:
            query = Project.all()
            
        for project in query:
            project_list.append(project.to_dict(head_only = True))
        self.response.out.write(utils.serialize(project_list))
            
    def post(self):
        
        project_dict = utils.deserialize(self.request.body)
        project = Project()
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.owner = self.user
        project.put()
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % project.uri()
        self.response.headers['Content-Location'] = '%s' % project.uri()
            
class ProjectResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, project_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, project_id):
        
        try:
            project = Project.get_by_id(int(project_id))            
        except:
            self.response.status = '404'
            
        self.response.out.write(utils.serialize(project.to_dict()))
                
    def put(self, project_id):
        
        project_dict = utils.deserialize(self.request.body)
        
        try:
            project = Project.get_by_id(int(project_id))
        except:
            self.response.status = '404'
            
        project.name = project_dict['name']
        project.description = project_dict['description']
        project.put()
        self.response.out.write(utils.serialize(project.to_dict()))
            
        
            
    def delete(self, project_id):
        
        try:
            project = Project.get_by_id(int(project_id))
        except:
            self.response.status = '404'
        
        project.delete()