import utils

from models import Image, Experiment
from handlers import OAuth2RESTJSONHandler
import webapp2

class ImageCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, expeirment_id):
        
        image_list = list()
        query = Image.all()
        for image in query:
            image_list.append(image.to_dict(head_only = True))
        self.response.out.write(utils.serialize(image_list))
        
    def post(self, experiment_id):
            
            experiment = Experiment.get_by_id(int(experiment_id))

            image_dict = utils.deserialize(self.request.body)

            image = Image()
            image.name = image_dict['name']
            image.description = image_dict['description']
            image.experiment = experiment
            image.owner = self.user
            image.put()

            self.response.status = '201'
            self.response.headers['Location'] = '%s' % image.uri()
            self.response.headers['Content-Location'] = '%s' % image.uri()
            self.response.out.write('{"uploadLink":"'+image.uri()+'"}')
            

class ImageResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id, image_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, experiment_id, image_id):
        
        try:
            image = Image.get_by_id(int(image_id))
            self.response.out.write(utils.serialize(image.to_dict()))
        
        except:
            self.response.status = '404'
                
    def put(self, experiment_id, image_id):
        
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
    
    def options(self, experiment_id, image_id):
        allowed_methods = ['POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
        
    def post(self, experiment_id, image_id):
        
        image = Image.get_by_id(int(image_id))
        imagefile = self.request.get('imagefile')
        from google.appengine.ext import db
        image.imagefile = db.Blob(imagefile)
        image.put()
            
        # this is supposed to produce output on an iframe (client-side) so I force an overwriting of the content-tyoe header
        import config
        self.response.headers['Content-Type'] = 'text/html; charset=%s' % config.CHARSET
        self.response.out.write('<html><body>SUCCESS! Download the file <a href="%s/download">here</a></body></html>' % image.uri())


class ImageDownloadHandler(OAuth2RESTJSONHandler):

    def options(self, experiment_id, image_id):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)

    def get(self, experiment_id, image_id):
        
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
                                
                                
                                
                                
                                
                                
                                
                                