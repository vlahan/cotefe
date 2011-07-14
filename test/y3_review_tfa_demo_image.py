import httplib2
import json
import logging
import sys
from datetime import date, datetime, timedelta
# from utils import *
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

# SERVER_URL = 'http://api.cotefe.net'
SERVER_URL = 'http://localhost:8080'

DESCRIPTION = 'CONET 3Y REVIEW TFA DEMO - PLEASE DO NOT DELETE'

IMAGEFILE_PATH_SUBSCRIBER = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'
IMAGEFILE_PATH_PUBLISHERS = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'
IMAGEFILE_PATH_INTERFERERS = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'

def main():
    
    logging.basicConfig(
        level=logging.DEBUG,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

    h = httplib2.Http()
    
    # GET THE FEDERATION
    
    logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    federation_dict = json.loads(content)
    logging.debug(federation_dict)
    
    # CREATE A PROJECT
    
    project_dict = {
        'name' : 'sample project',
        'description' : DESCRIPTION,
    }
    
    logging.info('creating a new project...')
    response, content = h.request(uri=federation_dict['projects'], method='POST', body=json.dumps(project_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    project_uri = response['content-location']
    logging.debug(project_uri)
    
    logging.info('getting the created project...')
    response, content = h.request(uri=response['content-location'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    project_dict = json.loads(content)
    logging.debug(project_dict)
    
    # CREATE AN EXPERIMENT
    
    experiment_dict = {
        'name' : 'sample experiment',
        'description' : DESCRIPTION,
        'project' : project_dict['id']
    }
    
    logging.info('creating a new experiment...')
    response, content = h.request(uri=federation_dict['experiments'], method='POST', body=json.dumps(experiment_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    experiment_uri = response['content-location']
    logging.debug(project_dict)
    
    logging.info('getting the created experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    # CREATE IMAGE FOR SUBCRIBER
    
    image_dict_subscriber = {
        'name' : 'image for subscriber',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id']
    }
    
    logging.info('uploading image for subscriber...')
    response, content = h.request(uri=federation_dict['images'], method='POST', body=json.dumps(image_dict_subscriber))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_subscriber = response['content-location']
    logging.debug(image_uri_subscriber)
    
    logging.info('getting image for subscriber...')
    response, content = h.request(uri=image_uri_subscriber, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_subscriber = json.loads(content)
    logging.debug(image_dict_subscriber)
    
    logging.info('uploading the actual image file for subscriber...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_SUBSCRIBER, 'rb')})
    request = urllib2.Request(image_dict_subscriber['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    # CREATE IMAGE FOR PUBLISHERS
    
    image_dict_publishers = {
        'name' : 'image for publishers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id']
    }
    
    logging.info('uploading image for publishers...')
    response, content = h.request(uri=federation_dict['images'], method='POST', body=json.dumps(image_dict_publishers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_publishers = response['content-location']
    logging.debug(image_uri_publishers)
    
    logging.info('getting image for publishers...')
    response, content = h.request(uri=image_uri_publishers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_publishers = json.loads(content)
    logging.debug(image_dict_publishers)
    
    logging.info('uploading the actual image file for publishers...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_PUBLISHERS, 'rb')})
    request = urllib2.Request(image_dict_publishers['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    # CREATING IMAGE FOR INTERFERERS
    
    image_dict_interferers = {
        'name' : 'image for interferers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id']
    }
    
    logging.info('uploading image for interferers...')
    response, content = h.request(uri=federation_dict['images'], method='POST', body=json.dumps(image_dict_interferers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_interferers = response['content-location']
    logging.debug(image_uri_interferers)
    
    logging.info('getting image for interferers...')
    response, content = h.request(uri=image_uri_subscriber, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_interferers = json.loads(content)
    logging.debug(image_dict_interferers)
    
    logging.info('uploading the actual image file...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_INTERFERERS, 'rb')})
    request = urllib2.Request(image_dict_interferers['upload'], datagen, headers)
    logging.info('200 OK')
    logging.debug(urllib2.urlopen(request).read())
    
    # GETTING THE UPDATED EXPERIMENT
    
    logging.info('getting the updated experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    logging.debug(experiment_dict['id'])

if __name__ == "__main__":
    main()
