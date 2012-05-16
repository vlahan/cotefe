from google.appengine.ext import db

import utils

from models import PropertySet, Experiment, Platform, VirtualNode
from handlers import OAuth2RESTJSONHandler

class PropertySetCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
            property_set_list = list()
            query = PropertySet.all().filter('experiment =', experiment)
            for property_set in query:
                property_set_list.append(property_set.to_dict(head_only = True))
            self.response.out.write(utils.serialize(property_set_list))
            
        except:
            self.response.status = '404'
            
    def post(self, experiment_id):
        
        try:
            experiment = Experiment.get_by_id(int(experiment_id))
        
            property_set_dict = utils.deserialize(self.request.body)
        
            platform = Platform.get_by_id(int(property_set_dict['platform_id']))
        
            property_set = PropertySet()
            property_set.name = property_set_dict['name']
            property_set.description = property_set_dict['description']
            property_set.owner = self.user
            property_set.experiment = experiment
            property_set.platform = platform
            property_set.num_nodes = property_set_dict['num_nodes']
            property_set.put()
        
            # now generate virtual nodes!
            
            # generate a list of virtual nodes
            
            vn_list = list()
        
            for k in range(1, property_set.num_nodes + 1):
                vn = VirtualNode()
                vn.name = 'virtual node #%s' % k
                vn.experiment = property_set.experiment
                vn.platform = property_set.platform
                vn.property_set = property_set
                vn.owner = self.user
                # vn.put()
                vn_list.append(vn)
                
            db.put(vn_list)
            
            self.response.status = '201'
            self.response.headers['Location'] = '%s' % property_set.uri()
            self.response.headers['Content-Location'] = '%s' % property_set.uri()
            
        except:
            self.response.status = '404'
            
class PropertySetResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, property_set_id):
        allowed_methods = ['GET', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, property_set_id):
        
        try:
            property_set = PropertySet.get_by_id(int(property_set_id))
            self.response.out.write(utils.serialize(property_set.to_dict()))
        
        except:
            self.response.status = '404'
            
    def delete(self, experiment_id, property_set_id):
        
        try:
            property_set = PropertySet.get_by_id(int(property_set_id))
            property_set.delete()
            
        except:
            self.response.status = '404'