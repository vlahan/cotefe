import utils

from models import Federation
from handlers import OAuth2RESTJSONHandler

class FederationResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
            
        try:
            federation = Federation.all().get()
            self.response.out.write(utils.serialize(federation.to_dict()))
        except:
            self.response.status = '404'