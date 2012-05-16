import utils

from models import Experiment, Project
from handlers import OAuth2RESTJSONHandler

class ExperimentCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        experiment_list = list()
        
        try:
            query = Experiment.all().filter('owner =', self.user)
        except:
            query = Experiment.all()
            
        for experiment in query:
            experiment_list.append(experiment.to_dict(head_only = True))
        self.response.out.write(utils.serialize(experiment_list))
            
    def post(self):
        
        experiment_dict = utils.deserialize(self.request.body)
        
        experiment = Experiment()
        
        experiment.name = experiment_dict['name']
        experiment.description = experiment_dict['description']
        experiment.owner = self.user
        experiment.project = Project.get_by_id(int(experiment_dict['project_id']))
        experiment.put()
        
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % experiment.uri()
        self.response.headers['Content-Location'] = '%s' % experiment.uri()
            
class ExperimentResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(utils.serialize(experiment.to_dict()))
        
    def put(self, experiment_id):
        
        experiment_dict = utils.deserialize(self.request.body)
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        except:
            self.response.status = '404'

        experiment.name = experiment_dict['name']
        experiment.description = experiment_dict['description']
        experiment.project = Project.get_by_id(int(experiment_dict['project_id']))
        experiment.put()
        
        self.response.out.write(utils.serialize(experiment.to_dict()))
        
        
    def delete(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        except:
            self.response.status = '404'
            
        experiment.delete()