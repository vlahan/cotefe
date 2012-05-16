import utils

from models import Testbed
from handlers import OAuth2RESTJSONHandler

class TestbedCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def get(self):
        
        testbed_list = list()
        for testbed in Testbed.all():
            testbed_list.append(testbed.to_dict(head_only = True))
        self.response.out.write(utils.serialize(testbed_list))

class TestbedResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, testbed_id):
        
        try:
            testbed = Testbed.get_by_key_name(testbed_id)        
        except:
            self.response.status = '404'
            
        self.response.out.write(utils.serialize(testbed.to_dict()))