import utils

from models import Job, Experiment, Testbed
from handlers import OAuth2RESTJSONHandler

class JobCollectionHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET', 'POST']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        testbeds = Testbed.all()
        
        for testbed in testbeds:
            
            testbed_jobs = get_all_jobs(testbed.server_url)
        
        collection = list()
        
        try:
            query = Job.all().filter('owner =', self.user)
        except:
            query = Job.all()
            
        for resource in query:
            collection.append(resource.to_dict(head_only = True))
        self.response.out.write(utils.serialize(collection))
            
    def post(self):
        
        resource_dict = utils.deserialize(self.request.body)
        
        resource = Job()
        
        resource.name = resource_dict['name']
        resource.description = resource_dict['description']
        resource.owner = self.user
        resource.experiment = Experiment.get_by_id(int(resource_dict['experiment_id']))
        resource.testbed = Testbed.get_by_key_name(resource_dict['testbed_id'])
        resource.datetime_from = utils.utc_string_to_utc_datetime(resource_dict['datetime_from'])
        resource.datetime_to = utils.utc_string_to_utc_datetime(resource_dict['datetime_to'])
        resource.put()
        
        self.response.status = '201'
        self.response.headers['Location'] = '%s' % resource.uri()
        self.response.headers['Content-Location'] = '%s' % resource.uri()
            
class JobResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self, experiment_id):
        allowed_methods = ['GET', 'PUT', 'DELETE']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self, job_id):
        
        try:
            resource = Job.get_by_id(int(job_id))        
        except:
            self.response.status = '404'
            
        self.response.out.write(utils.serialize(resource.to_dict()))
        
    def put(self, job_id):
        
        resource_dict = utils.deserialize(self.request.body)
        
        try:
            resource = Job.get_by_id(int(job_id))
        except:
            self.response.status = '404'

        resource.name = resource_dict['name']
        resource.description = resource_dict['description']
        resource.experiment = Experiment.get_by_id(int(resource_dict['experiment_id']))
        resource.testbed = Testbed.get_by_key_name(resource_dict['testbed_id'])
        resource.datetime_from = utils.utc_string_to_utc_datetime(resource_dict['datetime_from'])
        resource.datetime_to = utils.utc_string_to_utc_datetime(resource_dict['datetime_to'])
        resource.put()
        
        self.response.out.write(utils.serialize(resource.to_dict()))
        
        
    def delete(self, job_id):
        
        try:
            resource = Job.get_by_id(int(job_id))
        except:
            self.response.status = '404'
            
        resource.delete()