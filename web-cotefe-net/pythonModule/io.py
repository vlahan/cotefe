from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch

class MainPage(webapp.RequestHandler):
    def get(self):
        query=""
        method=""
        
        
        if self.request.get("method")!="":
            method=self.request.get("method")
        else:
            method="get"
        
        ##get method calls method=get    
        if self.request.get("query")=="platforms":
            query="platforms/"
        url = "https://api-cotefe-net.appspot.com/"+query
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(result.content)
        
        ##postmethod calls method=post
        
        ##postmethod calls method=put
        
        ##postmethod calls method=delete
        

application = webapp.WSGIApplication([('/io', MainPage)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
