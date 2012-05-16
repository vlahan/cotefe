import utils

from models import Image
from handlers import OAuth2RESTJSONHandler
import webapp2

class ImageCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        image_list = list()
        query = Image.all()
        for image in query:
            image_list.append(image.to_dict(head_only = True))
        self.response.out.write(utils.serialize(image_list))
        
    def post(self):
        
        try:

            image_dict = utils.deserialize(self.request.body)

            image = Image()
            image.name = image_dict['name']
            image.description = image_dict['description']
            image.owner = self.user
            image.put()

            self.response.status = '201'
            self.response.headers['Location'] = '%s' % image.uri()
            self.response.headers['Content-Location'] = '%s' % image.uri()
            
        except:
            self.response.status = '404'

class ImageResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, image_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            self.response.out.write(utils.serialize(image.to_dict()))
        
        except:
            self.response.status = '404'
                
    def put(self, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            image_dict = utils.deserialize(self.request.body)
            image.name = image_dict['name']
            image.description = image_dict['description']
            image.put()
            self.response.out.write(utils.serialize(image.to_dict()))
            
        except:
            self.response.status = '404'
            
    def delete(self, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            image.delete()
            
        except:
            self.response.status = '404'
            
class ImageUploadHandler(OAuth2RESTJSONHandler):
    
    def options(self, image_id):
        allowed_methods = ['POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def post(self, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            
        except:
            self.response.status = '404'
        
        try:
            imagefile = self.request.get('imagefile')
            image.imagefile = imagefile
            image.put()
            
            import config
            self.response.headers['Content-Type'] = 'text/html; charset=%s' % config.CHARSET
            
            self.response.out.write('<html><body>SUCCESS! Download the file <a href="%s/download">here</a></body></html>' % image.uri())
            
        except:
            self.response.status = '500'

class ImageDownloadHandler(OAuth2RESTJSONHandler):

    def options(self, image_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            self.response.headers['Content-Type'] = 'application/octet-stream'
            self.response.out.write(image.imagefile)
        
        except:
            self.response.status = '404'

class ImageUploadForm(webapp2.RequestHandler):
    
    def get(self):
        
        action_url = self.request.get('action_url')
        
        self.response.out.write('<html><body><form enctype="multipart/form-data" method="post" action="%s"><input type="file" name="imagefile" /><input type="submit" value="Upload" /></form></body></html>' % action_url)
                                
                                
                                
                                
                                
                                
                                
                                