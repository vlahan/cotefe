import utils

from models import VirtualNodeGroup, Experiment, VirtualNodeGroup2VirtualNode, VirtualNode
from handlers import OAuth2RESTJSONHandler

class VirtualNodeGroupCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            virtual_nodegroup_list = list()
            query = VirtualNodeGroup.all().filter('experiment =', experiment)
            for virtual_nodegroup in query:
                virtual_nodegroup_list.append(virtual_nodegroup.to_dict(head_only = True))
            self.response.out.write(utils.serialize(virtual_nodegroup_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            vng_dict = utils.deserialize(self.request.body)
        
            vng = VirtualNodeGroup()
            vng.name = vng_dict['name']
            vng.description = vng_dict['description']
            vng.owner = self.user
            vng.experiment = experiment
            vng.put()

            for vn_id in vng_dict['virtual_nodes']:
                VirtualNodeGroup2VirtualNode(vng = vng, vn = VirtualNode.get_by_id(int(vn_id))).put()
        
            self.response.status = '201'
            self.response.headers['Location'] = '%s' % vng.uri()
            self.response.headers['Content-Location'] = '%s' % vng.uri()
            
        except:
            self.response.status = '404'

class VirtualNodeGroupResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, virtual_nodegroup_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, virtual_nodegroup_id):
        
        try:
            virtual_nodegroup = VirtualNodeGroup.get_by_id(int(virtual_nodegroup_id))
            self.response.out.write(utils.serialize(virtual_nodegroup.to_dict()))
            
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, virtual_nodegroup_id):
        
        try:
            virtual_nodegroup = VirtualNodeGroup.get_by_id(int(virtual_nodegroup_id))
            virtual_nodegroup.delete()
            
        except:
            self.response.status = '404'