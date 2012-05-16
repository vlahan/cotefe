import utils

from models import VirtualNode, Experiment
from handlers import OAuth2RESTJSONHandler

class VirtualNodeCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_node_list = list()
            query = VirtualNode.all().filter('experiment =', experiment)
            for virtual_node in query:
                virtual_node_list.append(virtual_node.to_dict(head_only = True))
            self.response.out.write(utils.serialize(virtual_node_list))
            
        except:
            self.response.status = '404'

class VirtualNodeResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, virtual_node_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, virtual_node_id):
        
        try:
            virtual_node = VirtualNode.get_by_id(int(virtual_node_id))
            self.response.out.write(utils.serialize(virtual_node.to_dict()))
            
        except:
            self.response.status = '404'