#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

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
    
class TestbedResource(db.Model):
    
    
class JobCollectionHandler(webapp.RequestHandler):
  def get(self):
    result = urlfetch.fetch(
        method = 'GET',
        url = 'http://127.0.0.1:8000/jobs/',
    )
    self.response.set_status(200)
    self.response.out.write(result.content)
            
def main():
    application = webapp.WSGIApplication([
        ('/tasks/', TasksHandler),
        ('/tasks/456', TaskHandler),
        ('/reflector', Reflector),
        
        ('/jobs/', JobCollectionHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
