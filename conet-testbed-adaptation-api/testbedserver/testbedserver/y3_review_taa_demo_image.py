import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date
from utils import *
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

SERVER_URL = 'https://www.twist.tu-berlin.de:8001'
# SERVER_URL = 'http://localhost:8001'

DESCRIPTION = 'CONET 3Y REVIEW - PLEASE DO NOT DELETE'

IMAGEFILE_PATH = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    h = httplib2.Http()
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)

    image_dict = {
            'name' : 'sample image',
            'description' : DESCRIPTION,
        }
        
    logging.info('creating a new image...')
    response, content = h.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri = response['content-location']
    logging.debug(image_uri)
    
    logging.info('getting the information about the image...')
    response, content = h.request(uri=image_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict= json.loads(content)
    logging.debug(image_dict)
    
    logging.info('uploading the actual image file...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH, 'rb')})
    request = urllib2.Request(image_dict['upload_to'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
        
if __name__ == "__main__":
    main()