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

#    SERVER_URL = str(sys.argv[1])
#    PLATFORM = str(sys.argv[2])
#    JOB_URI = str(sys.argv[3])
    
    SERVER_URL = 'https://www.twist.tu-berlin.de:8001/'
    PLATFORM = 'TmoteSky'
    JOB_URI = 'https://www.twist.tu-berlin.de:8001/jobs/a95502ad'

    SINK_NODE_ID = 12
    
    DESCRIPTION = 'CONET 3Y REVIEW - PLEASE DO NOT DELETE'
    
    IMAGEFILE_PATH_SUBSCRIBER = '/Users/claudiodonzelli/Desktop/images/y3_review_image_subscriber'
    IMAGEFILE_PATH_PUBLISHERS = '/Users/claudiodonzelli/Desktop/images/y3_review_image_publishers'
    IMAGEFILE_PATH_INTERFERERS = '/Users/claudiodonzelli/Desktop/images/y3_review_image_interferers'

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
    
    assert len(job_dict['nodes']) == 96
    
    # GETTING THE NODES AND CREATING THE NODEGROUP ALL
    
    logging.info('getting the nodes for nodegroup including all nodes %s...' % (PLATFORM, ))
    response, content = h.request(uri='%s?platform=%s' % (testbed_dict['nodes'], PLATFORM), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list_all = json.loads(content)
    logging.debug(node_list_all)
    assert len(node_list_all) == 96
        
    nodegroup_dict_all = {
        'name' : 'subscriber',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list_all ],
        'job' : job_dict['id']
    }
    
    logging.info('creating the nodegroup for all nodes %s...' % (PLATFORM, ))    
    response, content = h.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_all))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_uri_all = response['content-location']
    logging.debug(nodegroup_uri_all)
    
    logging.info('getting the information about the created nodegroup all...')
    response, content = h.request(uri=nodegroup_uri_all, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_dict_all = json.loads(content)
    logging.debug(nodegroup_dict_all)
    assert len(nodegroup_dict_all['nodes']) == 96
    
    # GETTING THE NODES AND CREATING THE NODEGROUP SUBSCRIBER
    
    logging.info('getting the nodes for nodegroup subscriber (1 node)...')
    response, content = h.request(uri='%s?native_id=%d' % (testbed_dict['nodes'], SINK_NODE_ID), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list_subscriber = json.loads(content)
    logging.debug(node_list_subscriber)
    assert len(node_list_subscriber) == 1
        
    nodegroup_dict_subscriber = {
        'name' : 'subscriber',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list_subscriber ],
        'job' : job_dict['id']
    }
    
    logging.info('creating the nodegroup for subscriber...')    
    response, content = h.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_subscriber))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_uri_subscriber = response['content-location']
    logging.debug(nodegroup_uri_subscriber)
    
    logging.info('getting the information about the created nodegroup subscriber...')
    response, content = h.request(uri=nodegroup_uri_subscriber, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_dict_subscriber = json.loads(content)
    logging.debug(nodegroup_dict_subscriber)
    assert len(nodegroup_dict_subscriber['nodes']) == 1
    
    # GETTING THE NODES AND CREATING THE NODEGROUP PUBLISHERS
    
    logging.info('getting the nodes for nodegroup publishers (93 nodes)...')
    # node_blacklist = [ 59, 60, 274, 275, 62, 64, 276, 277, 171, 174, 278, 279]
    response, content = h.request(uri='%s?platform=%s&native_id__not_in=%d,%d,%d' % (testbed_dict['nodes'], PLATFORM, SINK_NODE_ID, 187, 90), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list_publishers = json.loads(content)
    logging.debug(node_list_publishers)
    logging.debug(len(node_list_publishers))
    assert len(node_list_publishers) == 93
        
    nodegroup_dict_publishers = {
        'name' : 'publishers',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list_publishers ],
        'job' : job_dict['id']
    }
    
    logging.info('creating a nodegroup publishers...')    
    response, content = h.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_publishers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_uri_publishers = response['content-location']
    logging.debug(nodegroup_uri_publishers)
    
    logging.info('getting the information about the created nodegroup publishers...')
    response, content = h.request(uri=nodegroup_uri_publishers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_dict_publishers = json.loads(content)
    logging.debug(nodegroup_dict_publishers)
    assert len(nodegroup_dict_publishers['nodes']) == 93
    
    # GETTING THE NODES AND CREATING THE NODEGROUP INTERFERERS
    
    logging.info('getting the nodes for nodegroup interferers (2 nodes)...')
    response, content = h.request(uri='%s?native_id__in=%d,%d' % (testbed_dict['nodes'], 187, 90), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list_interferers = json.loads(content)
    logging.debug(node_list_interferers)
    assert len(node_list_interferers) == 2
        
    nodegroup_dict_interferers = {
        'name' : 'interferers',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list_interferers ],
        'job' : job_dict['id']
    }
    
    logging.info('creating a nodegroup interferers...')    
    response, content = h.request(uri=testbed_dict['nodegroups'], method='POST', body=json.dumps(nodegroup_dict_interferers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_uri_interferers = response['content-location']
    logging.debug(nodegroup_uri_interferers)
    
    logging.info('getting the information about the created nodegroup interferers...')
    response, content = h.request(uri=nodegroup_uri_interferers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    nodegroup_dict_interferers = json.loads(content)
    logging.debug(nodegroup_dict_interferers)
    assert len(nodegroup_dict_interferers['nodes']) == 2
    
    # UPLOADING THE IMAGE FOR SUBSCRIBER
    
    image_dict_subscriber = {
            'name' : 'image for subscriber',
            'description' : DESCRIPTION,
        }
        
    logging.info('creating a new image resource...')
    response, content = h.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_subscriber))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_subscriber = response['content-location']
    logging.debug(image_uri_subscriber)
    
    logging.info('getting the information about the image for subscriber...')
    response, content = h.request(uri=image_uri_subscriber, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_subscriber= json.loads(content)
    logging.debug(image_dict_subscriber)
    
    logging.info('uploading the actual image file for subscriber...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_SUBSCRIBER, 'rb')})
    request = urllib2.Request(image_dict_subscriber['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    # UPLOADING THE IMAGE FOR PUBLISHERS
    
    image_dict_publishers = {
            'name' : 'image for publishers',
            'description' : DESCRIPTION,
        }
        
    logging.info('creating a new image resource...')
    response, content = h.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_publishers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_publishers = response['content-location']
    logging.debug(image_uri_publishers)
    
    logging.info('getting the information about the image for publishers...')
    response, content = h.request(uri=image_uri_publishers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_publishers= json.loads(content)
    logging.debug(image_dict_publishers)
    
    logging.info('uploading the actual image file for publishers...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_PUBLISHERS, 'rb')})
    request = urllib2.Request(image_dict_publishers['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    # UPLOADING THE IMAGE FOR INTERFERERS
    
    image_dict_interferers = {
            'name' : 'image for interferers',
            'description' : DESCRIPTION,
        }
        
    logging.info('creating a new image resource...')
    response, content = h.request(uri=testbed_dict['images'], method='POST', body=json.dumps(image_dict_interferers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_interferers = response['content-location']
    logging.debug(image_uri_interferers)
    
    logging.info('getting the information about the image for interferers...')
    response, content = h.request(uri=image_uri_interferers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_interferers= json.loads(content)
    logging.debug(image_dict_interferers)
    
    logging.info('uploading the actual image file for interferers...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_INTERFERERS, 'rb')})
    request = urllib2.Request(image_dict_interferers['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    ##########################################################################
    ##########################################################################
    ############# THIS CAN ONLY BE EXECUTED ON REAL NODES!! ##################
    ##########################################################################
    ##########################################################################
    
    # DELETING THE IMAGE FROM NODEGROUP ALL NODES
    
    logging.info('erasing image from the nodegroup all...')
    response, content = h.request(uri='%s/image' % nodegroup_uri_all, method='DELETE', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))

    # INSTALLING THE IMAGE TO NODEGROUP SUBSCRIBER
    
    logging.info('deploying the image to the nodegroup subscriber...')
    response, content = h.request(uri='%s/image/%s' % (nodegroup_uri_subscriber, image_dict_subscriber['id']), method='PUT', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    # INSTALLING THE IMAGE TO NODEGROUP PUBLISHERS
    
    logging.info('deploying the image to the nodegroup publishers...')
    response, content = h.request(uri='%s/image/%s' % (nodegroup_uri_publishers, image_dict_publishers['id']), method='PUT', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    # DELETING THE IMAGE FROM NODEGROUP INTERFERERS
    
#    logging.info('erasing image from the nodegroup interferers...')
#    response, content = h.request(uri='%s/image' % nodegroup_uri_interferers, method='DELETE', body='')
#    logging.debug(content)
#    assert response.status == 200
#    logging.info('%d %s' % (response.status, response.reason))
    
    raw_input('interferers are NOT activated - press ENTER to generate interference')
    
    # INSTALLING THE IMAGE TO NODEGROUP INTERFERERS
    
    logging.info('deploying the image to the nodegroup interferers...')
    response, content = h.request(uri='%s/image/%s' % (nodegroup_uri_interferers, image_dict_interferers['id']), method='PUT', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    raw_input('interferers are now activated - press ENTER to switch them off again')
    
    # DELETING THE IMAGE FROM NODEGROUP INTERFERERS
    
    logging.info('erasing the image from the nodegroup interferers...')
    response, content = h.request(uri='%s/image' % nodegroup_uri_interferers, method='DELETE', body='')
    logging.debug(content)
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    logging.info('DONE!')
    
if __name__ == "__main__":
    main()
