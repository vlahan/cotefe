import utils

from models import Sensor
from handlers import OAuth2RESTJSONHandler

class SensorCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        resource_list = list()
        query = Sensor.all()
        for resource in query:
            resource_list.append(resource.to_dict(head_only = True))
        self.response.out.write(utils.serialize(resource_list))
                
class SensorResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, resource_id):
        
        try:
            resource = Sensor.get_by_key_name(resource_id)
            self.response.out.write(utils.serialize(resource.to_dict()))      
        except:
            self.response.status = '404'