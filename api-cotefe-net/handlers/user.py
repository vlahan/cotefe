import utils

from models import User
from handlers import OAuth2RESTJSONHandler

class MeHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self):
        
        self.response.out.write(utils.serialize(self.user.to_dict()))        
        
# USER
            
class UserCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def get(self):
        
        user_list = list()
        for user in User.all():
            user_list.append(user.to_dict(head_only = True))
        self.response.out.write(utils.serialize(user_list))

class UserResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, user_id):
        
        try:
            user = User.get_by_id(int(user_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(utils.serialize(user.to_dict()))