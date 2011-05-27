class TasksHandler(webapp.RequestHandler):
    def post(self):
        taskqueue.add(
            method = 'POST',
            url = '/reflector',
            params = {
                'method' : 'PUT',
                'url' : 'http://127.0.0.1:8081/nodegroups/123',
            }
        )
        self.response.set_status(201)
        self.response.out.write('New Task created at <a href="http://localhost:8080/tasks/456">http://localhost:8080/tasks/456</a>\n')
    
class TaskHandler(webapp.RequestHandler):
    def get(self):
        self.response.set_status(200)
        self.response.out.write('Task ID = 456, Method = PUT, URL = http://localhost:8000/nodegroups/123\n')

class Reflector(webapp.RequestHandler):
    def post(self):
        # logging.info(self.request.get('method'))
        # logging.info(self.request.get('url'))
        result = urlfetch.fetch(
            method = self.request.get('method'),
            url = self.request.get('url'),
        )