import httplib2
import json
import logging
import sys
from datetime import date, datetime, timedelta
from utils import *
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

SERVER_URL = 'http://api.cotefe.net'
PLATFORM = 'TmoteSky'

DESCRIPTION = 'CONET 3Y REVIEW TFA DEMO - PLEASE DO NOT DELETE'
SUBSCRIBER = 1
PUBLISHERS = 99
INTERFERERS = 2

N = SUBSCRIBER + PUBLISHERS + INTERFERERS

IMAGEFILE_PATH_SUBSCRIBER = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'
IMAGEFILE_PATH_PUBLISHERS = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'
IMAGEFILE_PATH_INTERFERERS = '/Users/claudiodonzelli/Desktop/images/blink_test_image_telosb'

def main():
    
    logging.basicConfig(
        level=logging.INFO,
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
    
    # GET THE PLATFORM
    
    logging.info('getting the platform with name \"%s\"...' % PLATFORM)
    response, content = h.request(uri='%s%s' % (federation_dict['platforms'], PLATFORM), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_dict = json.loads(content)
    logging.debug(platform_dict)
    
    # CREATE A PROPERTY SET
    
    property_set_dict = {
        'name' : 'sample property set',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'platform' : platform_dict['id'],
        'node_count' : N
    }
    
    logging.info('creating a new property set made of %d nodes of platform %s...' % (N, PLATFORM))
    response, content = h.request(uri=federation_dict['property_sets'], method='POST', body=json.dumps(property_set_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    property_set_uri = response['content-location']
    logging.debug(property_set_uri)
    
    logging.info('getting the created property set (including the created virtual nodes)...')
    response, content = h.request(uri=property_set_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    property_set_dict = json.loads(content)
    logging.debug(property_set_dict)
    
    # GETTING THE EXPERIMENT AGAIN
    
    logging.info('getting the updated experiment (including virtual nodes)...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    # GETTING THE VIRTUAL NODES
    
    logging.info('getting the virtual nodes for experiment...')
    response, content = h.request(uri='%s?experiment=%s' % (federation_dict['virtual_nodes'], experiment_dict['id']), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_node_list = json.loads(content)
    logging.debug(virtual_node_list)
    
    # CHECK THAT YOU GET EXACTLY THE RIGHT NUMBER OF VIRTUAL NODES
    
    assert len(virtual_node_list) == 102
    
    # SLICE THE VIRTUAL NODES IN 3 VIRTUAL GROUPS
    
    virtual_node_list_subscriber = virtual_node_list[0:1]
    virtual_node_list_publishers = virtual_node_list[1:100]
    virtual_node_list_interferers = virtual_node_list[100:]
    
    # CHECK AGAIN THE NUMBER OF NODES
    
    assert len(virtual_node_list_subscriber) == SUBSCRIBER
    assert len(virtual_node_list_publishers) == PUBLISHERS
    assert len(virtual_node_list_interferers) == INTERFERERS
    
    # CREATE 3 LISTS OF NODE IDS ACCORDING TO THE GROUPS 
    
    virtual_node_id_list_subscriber = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_subscriber ]
    virtual_node_id_list_publishers = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_publishers ]
    virtual_node_id_list_interferers = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_interferers ]

    # CHECK AGAIN
    
    assert len(virtual_node_id_list_subscriber) == SUBSCRIBER
    assert len(virtual_node_id_list_publishers) == PUBLISHERS
    assert len(virtual_node_id_list_interferers) == INTERFERERS
    
    # CREATING THE FIRST VIRTUAL NDEGROUP
    
    virtual_nodegroup_dict_subscriber = {
        'name' : 'subscribers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_subscriber
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (SUBSCRIBER))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_subscriber))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_subscribers = response['content-location']
    logging.debug(virtual_nodegroup_uri_subscribers)
    
    logging.info('getting the virtual nodegroup subscribers...')
    response, content = h.request(uri=virtual_nodegroup_uri_subscribers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_subscribers = json.loads(content)
    logging.debug(virtual_nodegroup_dict_subscribers)
    
    assert len(virtual_nodegroup_dict_subscriber['virtual_nodes']) == SUBSCRIBER
    
    # CREATING THE SECOND VIRTUAL NODEGROUP
    
    virtual_nodegroup_dict_publishers = {
        'name' : 'publishers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_publishers
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (PUBLISHERS))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_publishers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_publishers = response['content-location']
    logging.debug(virtual_nodegroup_uri_publishers)
    
    logging.info('getting the virtual nodegroup publishers...')
    response, content = h.request(uri=virtual_nodegroup_uri_publishers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_publishers = json.loads(content)
    logging.debug(virtual_nodegroup_dict_publishers)
    
    assert len(virtual_nodegroup_dict_publishers['virtual_nodes']) == PUBLISHERS
    
    # CREATING THE THIRD VIRTUAL NODEGROUP
    
    virtual_nodegroup_dict_interferers = {
        'name' : 'interferers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_interferers
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (INTERFERERS))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_interferers))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_interferers = response['content-location']
    logging.debug(virtual_nodegroup_uri_interferers)
    
    logging.info('getting the virtual nodegroup interferers...')
    response, content = h.request(uri=virtual_nodegroup_uri_interferers, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_interferers = json.loads(content)
    logging.debug(virtual_nodegroup_dict_interferers)
    
    assert len(virtual_nodegroup_dict_interferers['virtual_nodes']) == INTERFERERS
    
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
    
    # UPLOADING THE 3 IMAGE FILES
    
#    logging.info('uploading the actual image file for subscriber...')
#    register_openers()
#    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_SUBSCRIBER, 'rb')})
#    request = urllib2.Request(image_dict_subscriber['upload_to'], datagen, headers)
#    logging.info('200 OK')
#    logging.debug(urllib2.urlopen(request).read())
#    
#    logging.info('uploading the actual image file for publishers...')
#    register_openers()
#    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_PUBLISHERS, 'rb')})
#    request = urllib2.Request(image_dict_publishers['upload_to'], datagen, headers)
#    logging.info('200 OK')
#    logging.debug(urllib2.urlopen(request).read())
#    
#    logging.info('uploading the actual image file...')
#    register_openers()
#    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_INTERFERERS, 'rb')})
#    request = urllib2.Request(image_dict_interferers['upload_to'], datagen, headers)
#    logging.info('200 OK')
#    logging.debug(urllib2.urlopen(request).read())
    
    # GETTING THE UPDATED EXPERIMENT
    
    logging.info('getting the updated experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    # LIST OF TESTBEDS SUPPORTING THIS EXPERIMENT
    
    logging.info('getting the list of testbeds supporting this experiment (according to property_sets)...')
    response, content = h.request(uri='%s?supports_experiment=%s' % (federation_dict['testbeds'], experiment_dict['id']), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_list = json.loads(content)
    logging.debug(testbed_list)
    
    logging.info('choosing the first testbed on the list (TWIST)...')
    testbed_dict = testbed_list[0]
    
    exit()
    
    # GETTING THE LIST OF COLLIDING JOBS
    
#    dt_now = datetime.now()
#    dt_next_month = dt_now + timedelta(days=30)
#    str_now = berlin_datetime_to_utc_string(dt_now)
#    str_next_month = berlin_datetime_to_utc_string(dt_next_month)
#    logging.debug(str_now)
#    logging.debug(str_next_month)
    
    d_from = date.today()
    d_to = d_from + timedelta(days=9)
    
    logging.debug(d_from)
    logging.debug(d_to)
    
    logging.info('getting the reserved jobs for the available testbed between date %s and date %s (an attempt to create a non-overlapping job should be then successful)' % (d_from, d_to))
    response, content = h.request(uri='%s?supports_experiment=%s&testbed=%s&date_from=%s&date_to=%s' % (federation_dict['jobs'], experiment_dict['id'], testbed_dict['id'], d_from, d_to), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_list = json.loads(content)
    logging.debug(job_list)
    
    # DEFINING VIRTUAL TASK 1 INSTALL IMAGE 1 ON VIRTUAL NODEGROUP 1
    
    # DEFINING VIRTUAL TASK 1 INSTALL IMAGE 2 ON VIRTUAL NODEGROUP 2
    
    # DEFINING VIRTUAL TASK 1 INSTALL IMAGE 3 ON VIRTUAL NODEGROUP 3

    
#    logging.info('installing image 1 on virtual nodegroup 1...')
#    response, content = h.request(uri='%s%s/image/%s' % (federation_dict['virtual_nodegroups'], virtual_nodegroup_dict_1['id'], image_dict_1['id']), method='PUT', body='', headers = {'Content-Length': '0'})
#    assert response.status == 200
#    logging.info('%d %s' % (response.status, response.reason))
#    
#    logging.info('installing image 2 on virtual nodegroup 2...')
#    response, content = h.request(uri='%s%s/image/%s' % (federation_dict['virtual_nodegroups'], virtual_nodegroup_dict_2['id'], image_dict_2['id']), method='PUT', body='', headers = {'Content-Length': '0'})
#    assert response.status == 200
#    logging.info('%d %s' % (response.status, response.reason))

if __name__ == "__main__":
    main()
