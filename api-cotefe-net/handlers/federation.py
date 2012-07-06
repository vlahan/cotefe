from collections import OrderedDict

import config
import utils

from handlers import OAuth2RESTJSONHandler

class FederationResourceHandler(OAuth2RESTJSONHandler):
    
    def options(self):
        allowed_methods = ['GET']
        OAuth2RESTJSONHandler.options(self, allowed_methods)
    
    def get(self):
        
        r = OrderedDict()
        r['uri'] =          '%s/' % config.FEDERATION_SERVER_URL
        r['media_type'] =   config.MEDIA_TYPE
        r['name'] =         config.FEDERATION_NAME
        r['description'] =  config.FEDERATION_DESCRIPTION
        r['users'] =        '%s/%s/' % (config.FEDERATION_SERVER_URL, 'users')
        r['testbeds'] =     '%s/%s/' % (config.FEDERATION_SERVER_URL, 'testbeds')
        r['platforms'] =    '%s/%s/' % (config.FEDERATION_SERVER_URL, 'platforms')
        r['projects'] =     '%s/%s/' % (config.FEDERATION_SERVER_URL, 'projects')
        r['experiments'] =  '%s/%s/' % (config.FEDERATION_SERVER_URL, 'experiments')
        # r['jobs'] =         '%s/%s/' % (config.FEDERATION_SERVER_URL, 'jobs')
        
        self.response.out.write(utils.serialize(r))
        
        # # # # INTRODUCING CACHING # # # # #
        
        from wsgiref.handlers import format_date_time
        import datetime
        import time
        from time import mktime
        
        # freshness lifetime (sec)
        fl = 1800
        
        # introducing artificial delay
        time.sleep(5)
        
        # current datetime
        now = datetime.datetime.now()
        
        # no need to add the Date header because GAE adds it by defaul
        # date = mktime(now.timetuple())
        # self.response.headers['Date'] = format_date_time(date)
        
        # HTTP/1.0 header
        expires = now + datetime.timedelta(0, fl)
        stamp = mktime(expires.timetuple())
        self.response.headers['Expires'] = format_date_time(stamp)
        
        # HTTP/1.1 header
        self.response.headers['Cache-control'] = 'max-age=%s, must-revalidate' % fl # HTTP 1.1
        
        # # # # # # # # # # # # # # # # # # #
