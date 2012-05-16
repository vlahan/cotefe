import utils

from models import VirtualTask, Experiment
from handlers import OAuth2RESTJSONHandler

class VirtualTaskCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_task_list = list()
            query = VirtualTask.all().filter('experiment =', experiment)
            for virtual_task in query:
                virtual_task_list.append(virtual_task.to_dict(head_only = True))
            self.response.out.write(utils.serialize(virtual_task_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
            
            vt_dict = utils.deserialize(self.request.body)

            vt = VirtualTask()
            vt.name = vt_dict['name']
            vt.description = vt_dict['description']
            vt.method = vt_dict['method']
            vt.target = vt_dict['target']
            vt.owner = self.user
            vt.experiment = experiment
            vt.put()

            self.response.status = '201'
            self.response.headers['Location'] = '%s' % vt.uri()
            self.response.headers['Content-Location'] = '%s' % vt.uri()
            
        except:
            self.response.status = '404'

class VirtualTaskResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, vt_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, vt_id):
        
        try:
            vt = VirtualTask.get_by_id(int(vt_id))
            self.response.out.write(utils.serialize(vt.to_dict()))
        
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, vt_id):
        
        try:
            vt = VirtualTask.get_by_id(int(vt_id))
            vt.delete()
        
        except:
            self.response.status = '404'