from piston.handler import BaseHandler
from api.models import Testbed, Job

class TestbedHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Testbed
    
class JobHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Job
