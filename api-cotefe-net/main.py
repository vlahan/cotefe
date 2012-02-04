import logging
import webapp2

import config
from routes import routes

session_config = {}
session_config['webapp2_extras.sessions'] = { 'secret_key': 'cotefe' }

app = webapp2.WSGIApplication(routes, debug=config.DEBUG, config=session_config)

def main():
    app.run()


if __name__ == '__main__':
    main()