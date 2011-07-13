import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date
from utils import *
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

DESCRIPTION = 'CONET 3Y REVIEW - PLEASE DO NOT DELETE'
IMAGEFILE_PATH = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    try:
        SERVER_URL = str(sys.argv[1])
        JOB_URI = str(sys.argv[2])
    except Exception:
        print 'Usage: python %s SERVER_URL JOB_URI' % __file__
        print 'Example: python %s https://www.twist.tu-berlin.de:8001 https://www.twist.tu-berlin.de:8001/jobs/af2ebeba' % __file__
        sys.exit()

    h = httplib2.Http()
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)
    
    logging.info('getting the information about the created job...')
    response, content = h.request(uri=JOB_URI, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_dict = json.loads(content)
    logging.debug(job_dict)
        
    nodegroup_dict = {
        'name' : 'sample node group',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in job_dict['nodes'] ],
        'job' : job_dict['id']
    }
    
    logging.info('creating a nodegroup..')    
    response, content = h.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_uri = response['content-location']
    logging.debug(nodegroup_uri)
    
    logging.info('getting the information about the created nodegroup...')
    response, content = h.request(uri=nodegroup_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_dict = json.loads(content)
    logging.debug(nodegroup_dict)
    
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
    
    logging.info('deploying the image to the nodegroup...')
    response, content = h.request(uri='%s/image/%s' % (nodegroup_uri, image_dict['id']), method='PUT', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    logging.info('erasing the image from the nodegroup...')
    response, content = h.request(uri='%s/image' % nodegroup_uri, method='DELETE', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
if __name__ == "__main__":
    main()
