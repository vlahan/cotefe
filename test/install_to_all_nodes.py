import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import time

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

    SERVER_URL = str(sys.argv[1])
    JOB_URI = str(sys.argv[2])
    
    NATIVE_ID = 12

    DESCRIPTION = 'CONET 3Y REVIEW - PLEASE DO NOT DELETE'
    
    PLATFORM = 'eyesIFXv20'

    IMAGEFILE_PATH = '/Users/claudiodonzelli/Desktop/images/testserial.exe'

    h = httplib2.Http()
    
    # GETTING THE TESTBED
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)
    
    # GETTING THE JOB (INCLUDING NODES)
    
    logging.info('getting the information about the created job...')
    response, content = h.request(uri=JOB_URI, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_dict = json.loads(content)
    logging.debug(job_dict)
    
    # GETTING THE NODES AND CREATING THE NODEGROUP
    
    logging.info('getting the nodes for nodegroup...')
    response, content = h.request(uri='%s?platform=%s' % (testbed_dict['nodes'], PLATFORM), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list = json.loads(content)
    logging.info(len(node_list))
    # assert len(node_list) == 102
        
    nodegroup_dict = {
        'name' : 'all nodes',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list ],
        'job' : job_dict['id']
    }
    
    logging.info('creating the nodegroup...')    
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
    # assert len(nodegroup_dict['nodes']) == 102

    
    # UPLOADING THE IMAGE
    
    image_dict = {
            'name' : 'image for all nodes',
            'description' : DESCRIPTION,
        }
        
    logging.info('creating a new image resource...')
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
    request = urllib2.Request(image_dict['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    ##########################################################################
    ##########################################################################
    ############# THIS CAN ONLY BE EXECUTED ON REAL NODES!! ##################
    ##########################################################################
    ##########################################################################
    
    # INSTALLING THE IMAGE TO NODEGROUP PUBLISHERS
    
    logging.info('erasing the image from the nodegroup...')
    response, content = h.request(uri='%s/image' % (nodegroup_uri, ), method='DELETE', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    exit()
    
    time.sleep(60)
    
    logging.info('deploying the image to the nodegroup...')
    response, content = h.request(uri='%s/image/%s' % (nodegroup_uri, image_dict['id']), method='PUT', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    logging.info('DONE!')
    
if __name__ == "__main__":
    main()
