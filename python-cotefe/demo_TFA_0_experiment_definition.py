import httplib2
import json
import logging
import sys
from datetime import date, datetime, timedelta
# from poster.encode import multipart_encode
# from poster.streaminghttp import register_openers
import urllib2
import webbrowser

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    PLATFORM = 'TmoteSky'

    DESCRIPTION = 'TWIST RESTful API DEMO - PLEASE DO NOT DELETE!'
    SUBSCRIBER = 1
    PUBLISHERS = 93
    INTERFERERS = 2
    
    N = SUBSCRIBER + PUBLISHERS + INTERFERERS

    IMAGEFILE_PATH_SUBSCRIBER = '../images/demo_image_subscriber_ctp'
    IMAGEFILE_PATH_PUBLISHERS = '../images/demo_image_publishers_ctp'
    IMAGEFILE_PATH_INTERFERERS = '../images/demo_image_interferers'

    h = httplib2.Http()
    
    # GET THE FEDERATION
    
    logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    federation_dict = json.loads(content)
    # logging.debug(federation_dict)
    
    # CREATE A PROJECT
    
    project_dict = {
        'name' : 'sample project',
        'description' : DESCRIPTION,
    }
    
    # logging.info('creating a new project...')
    response, content = h.request(uri=federation_dict['projects'], method='POST', body=json.dumps(project_dict))
    # logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    project_uri = response['content-location']
    # logging.debug(project_uri)
    
    # logging.info('getting the created project...')
    response, content = h.request(uri=response['content-location'], method='GET', body='')
    # logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    project_dict = json.loads(content)
    # logging.debug(project_dict)
    
    # CREATE AN EXPERIMENT
    
    experiment_dict = {
        'name' : 'sample experiment',
        'description' : DESCRIPTION,
        'project' : project_dict['id']
    }
    
    logging.info('creating a new experiment...')
    response, content = h.request(uri=federation_dict['experiments'], method='POST', body=json.dumps(experiment_dict))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    experiment_uri = response['content-location']
    logging.debug(experiment_uri)
    
    logging.info('getting the created experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    # GET THE PLATFORM
    
    logging.info('getting the platform with name \"%s\"...' % PLATFORM)
    response, content = h.request(uri='%s%s' % (federation_dict['platforms'], PLATFORM), method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    platform_dict = json.loads(content)
    logging.debug(platform_dict)
    
    # CREATE A PROPERTY SET
    
    property_set_dict = {
        'name' : 'sample property set',
        'description' : DESCRIPTION,
        'platform' : platform_dict['id'],
        'virtual_node_count' : N,
    }
    
    logging.info('creating a new property set made of %d nodes of platform %s...' % (N, PLATFORM))
    response, content = h.request(uri='%s/property-sets/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(property_set_dict))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    property_set_uri = response['content-location']
    logging.debug(property_set_uri)
    
    logging.info('getting the created property set (including the created virtual nodes)...')
    response, content = h.request(uri=property_set_uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    property_set_dict = json.loads(content)
    logging.debug(property_set_dict)
    
    # GETTING THE VIRTUAL NODES
    
    logging.info('getting the virtual nodes for experiment...')
    response, content = h.request(uri='%s/virtual-nodes/' % (experiment_dict['uri'], ), method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_node_list = json.loads(content)
    logging.debug(virtual_node_list)
    
    # CHECK THAT YOU GET EXACTLY THE RIGHT NUMBER OF VIRTUAL NODES
    
    assert len(virtual_node_list) == 96
    
    # SLICE THE VIRTUAL NODES IN 3 VIRTUAL GROUPS
    
    virtual_node_list_subscriber = virtual_node_list[0:1]
    virtual_node_list_publishers = virtual_node_list[1:94]
    virtual_node_list_interferers = virtual_node_list[94:]
    
    # CHECK AGAIN THE NUMBER OF NODES
    
    assert len(virtual_node_list_subscriber) == SUBSCRIBER
    assert len(virtual_node_list_publishers) == PUBLISHERS
    assert len(virtual_node_list_interferers) == INTERFERERS
    
    # CREATE 3 LISTS OF NODE IDS ACCORDING TO THE GROUPS 
    
#    virtual_node_id_list_subscriber = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_subscriber ]
#    virtual_node_id_list_publishers = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_publishers ]
#    virtual_node_id_list_interferers = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_interferers ]
    
    virtual_node_id_list_all = [ virtual_node_dict['id'] for virtual_node_dict in virtual_node_list ]
    virtual_node_id_list_subscriber = [ virtual_node_dict['id'] for virtual_node_dict in virtual_node_list_subscriber ]
    virtual_node_id_list_publishers = [ virtual_node_dict['id'] for virtual_node_dict in virtual_node_list_publishers ]
    virtual_node_id_list_interferers = [ virtual_node_dict['id'] for virtual_node_dict in virtual_node_list_interferers ]

    # CHECK AGAIN
    
    assert len(virtual_node_id_list_subscriber) == SUBSCRIBER
    assert len(virtual_node_id_list_publishers) == PUBLISHERS
    assert len(virtual_node_id_list_interferers) == INTERFERERS
    
    # CREATING THE A VIRTUAL NODEGROUP WITH ALL NODES
    
    virtual_nodegroup_dict_all = {
        'name' : 'all nodes',
        'description' : DESCRIPTION,
        'virtual_nodes' : virtual_node_id_list_all,
    }
    
    logging.info('creating a virtual nodegroup out of all virtual nodes...')
    response, content = h.request(uri='%s/virtual-nodegroups/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_nodegroup_dict_all))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_nodegroup_uri_all = response['content-location']
    logging.debug(virtual_nodegroup_uri_all)
    
    logging.info('getting the virtual nodegroup all nodes...')
    response, content = h.request(uri=virtual_nodegroup_uri_all, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_nodegroup_dict_all = json.loads(content)
    logging.debug(virtual_nodegroup_dict_all)
    
    assert len(virtual_nodegroup_dict_all['virtual_nodes']) == N
    
    # CREATING THE FIRST VIRTUAL NODEGROUP
    
    virtual_nodegroup_dict_subscriber = {
        'name' : 'subscribers',
        'description' : DESCRIPTION,
        'virtual_nodes' : virtual_node_id_list_subscriber,
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (SUBSCRIBER))
    response, content = h.request(uri='%s/virtual-nodegroups/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_nodegroup_dict_subscriber))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_nodegroup_uri_subscriber = response['content-location']
    logging.debug(virtual_nodegroup_uri_subscriber)
    
    logging.info('getting the virtual nodegroup subscribers...')
    response, content = h.request(uri=virtual_nodegroup_uri_subscriber, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_nodegroup_dict_subscriber = json.loads(content)
    logging.debug(virtual_nodegroup_dict_subscriber)
    
    assert len(virtual_nodegroup_dict_subscriber['virtual_nodes']) == SUBSCRIBER
    
    # CREATING THE SECOND VIRTUAL NODEGROUP
    
    virtual_nodegroup_dict_publishers = {
        'name' : 'publishers',
        'description' : DESCRIPTION,
        'virtual_nodes' : virtual_node_id_list_publishers,
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (PUBLISHERS))
    response, content = h.request(uri='%s/virtual-nodegroups/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_nodegroup_dict_publishers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_nodegroup_uri_publishers = response['content-location']
    logging.debug(virtual_nodegroup_uri_publishers)
    
    logging.info('getting the virtual nodegroup publishers...')
    response, content = h.request(uri=virtual_nodegroup_uri_publishers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_nodegroup_dict_publishers = json.loads(content)
    logging.debug(virtual_nodegroup_dict_publishers)
    
    assert len(virtual_nodegroup_dict_publishers['virtual_nodes']) == PUBLISHERS
    
    # CREATING THE THIRD VIRTUAL NODEGROUP
    
    virtual_nodegroup_dict_interferers = {
        'name' : 'interferers',
        'description' : DESCRIPTION,
        'virtual_nodes' : virtual_node_id_list_interferers,
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (INTERFERERS))
    response, content = h.request(uri='%s/virtual-nodegroups/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_nodegroup_dict_interferers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_nodegroup_uri_interferers = response['content-location']
    logging.debug(virtual_nodegroup_uri_interferers)
    
    logging.info('getting the virtual nodegroup interferers...')
    response, content = h.request(uri=virtual_nodegroup_uri_interferers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_nodegroup_dict_interferers = json.loads(content)
    logging.debug(virtual_nodegroup_dict_interferers)
    
    assert len(virtual_nodegroup_dict_interferers['virtual_nodes']) == INTERFERERS
    
    # CREATE IMAGE FOR SUBCRIBER
    
    image_dict_subscriber = {
        'name' : 'SUBSCRIBER',
        'description' : DESCRIPTION,
    }
    
    logging.info('uploading image for subscriber...')
    response, content = h.request(uri='%s/images/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(image_dict_subscriber))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    image_uri_subscriber = response['content-location']
    logging.debug(image_uri_subscriber)
    
    logging.info('getting image for subscriber...')
    response, content = h.request(uri=image_uri_subscriber, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    image_dict_subscriber = json.loads(content)
    logging.debug(image_dict_subscriber)
    
    logging.info('uploading the actual image file for subscriber...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_SUBSCRIBER, 'rb')})
    request = urllib2.Request(image_dict_subscriber['upload'], datagen, headers)
    logging.debug(urllib2.urlopen(request).read())
    logging.info('200 OK')
    
    # CREATE IMAGE FOR PUBLISHERS
    
    image_dict_publishers = {
        'name' : 'PUBLISHER',
        'description' : DESCRIPTION,
    }
    
    logging.info('uploading image for publishers...')
    response, content = h.request(uri='%s/images/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(image_dict_publishers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    image_uri_publishers = response['content-location']
    logging.debug(image_uri_publishers)
    
    logging.info('getting image for publishers...')
    response, content = h.request(uri=image_uri_publishers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    image_dict_publishers = json.loads(content)
    logging.debug(image_dict_publishers)
    
    logging.info('uploading the actual image file for publishers...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_PUBLISHERS, 'rb')})
    request = urllib2.Request(image_dict_publishers['upload'], datagen, headers)
    logging.debug(urllib2.urlopen(request).read())
    logging.info('200 OK')
    
    # CREATING IMAGE FOR INTERFERERS
    
    image_dict_interferers = {
        'name' : 'INTERFERER',
        'description' : DESCRIPTION,
    }
    
    logging.info('uploading image for interferers...')
    response, content = h.request(uri='%s/images/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(image_dict_interferers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    image_uri_interferers = response['content-location']
    logging.debug(image_uri_interferers)
    
    logging.info('getting image for interferers...')
    response, content = h.request(uri=image_uri_interferers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    image_dict_interferers = json.loads(content)
    logging.debug(image_dict_interferers)
    
    logging.info('uploading the actual image file...')
    register_openers()
    datagen, headers = multipart_encode({'imagefile': open(IMAGEFILE_PATH_INTERFERERS, 'rb')})
    request = urllib2.Request(image_dict_interferers['upload'], datagen, headers)
    logging.debug(urllib2.urlopen(request).read())
    logging.info('200 OK')
    
    # DEFINING VIRTUAL TASK 1 ERASE ALL NODES
    
    virtual_task_dict_erase_all = {
        'name' : 'erase all nodes',
        'description' : DESCRIPTION,
        'step' : 1,
        'method' : 'DELETE',
        'target' : '%s/image' % (virtual_nodegroup_dict_all['uri'], )
    }
    
    logging.info('creating virtual task: installing image on virtual nodegroup subscriber...')
    response, content = h.request(uri='%s/virtual-tasks/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_task_dict_erase_all))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_task_uri_erase_all = response['content-location']
    logging.debug(virtual_task_uri_erase_all)
    
    logging.info('getting the created virtual task...')
    response, content = h.request(uri=virtual_task_uri_erase_all, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_task_dict_erase_all = json.loads(content)
    logging.debug(virtual_task_dict_erase_all)
    
    # DEFINING VIRTUAL TASK 1 INSTALL IMAGE 1 ON VIRTUAL NODEGROUP 1
    
    virtual_task_dict_subscriber = {
        'name' : 'install image on subscriber node',
        'description' : DESCRIPTION,
        'step' : 2,
        'method' : 'PUT',
        'target' : '%s/image/%s' % (virtual_nodegroup_dict_subscriber['uri'], image_dict_subscriber['id'])
    }
    
    logging.info('creating virtual task: installing image on virtual nodegroup subscriber...')
    response, content = h.request(uri='%s/virtual-tasks/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_task_dict_subscriber))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_task_uri_subscriber = response['content-location']
    logging.debug(virtual_task_uri_subscriber)
    
    logging.info('getting the created virtual task...')
    response, content = h.request(uri=virtual_task_uri_subscriber, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_task_dict_subscriber = json.loads(content)
    logging.debug(virtual_task_dict_subscriber)
    
    # DEFINING VIRTUAL TASK 2 INSTALL IMAGE 2 ON VIRTUAL NODEGROUP 2
    
    virtual_task_dict_publishers = {
        'name' : 'install image on publishers node',
        'description' : DESCRIPTION,
        'step' : 3,
        'method' : 'PUT',
        'target' : '%s/image/%s' % (virtual_nodegroup_dict_publishers['uri'], image_dict_publishers['id'])
    }
    
    logging.info('creating virtual task: installing image on virtual nodegroup publishers...')
    response, content = h.request(uri='%s/virtual-tasks/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_task_dict_publishers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_task_uri_publishers = response['content-location']
    logging.debug(virtual_task_uri_publishers)
    
    logging.info('getting the created virtual task...')
    response, content = h.request(uri=virtual_task_uri_publishers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_task_dict_publishers = json.loads(content)
    logging.debug(virtual_task_dict_publishers)
    
    # DEFINING VIRTUAL TASK 3 INSTALL IMAGE 3 ON VIRTUAL NODEGROUP 3
    
    virtual_task_dict_interferers = {
        'name' : 'install image on interferers node',
        'description' : DESCRIPTION,
        'step' : 4,
        'method' : 'PUT',
        'target' : '%s/image/%s' % (virtual_nodegroup_dict_interferers['uri'], image_dict_interferers['id'])
    }
    
    logging.info('creating virtual task: installing image on virtual nodegroup interferers...')
    response, content = h.request(uri='%s/virtual-tasks/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_task_dict_interferers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_task_uri_interferers = response['content-location']
    logging.debug(virtual_task_uri_interferers)
    
    logging.info('getting the created virtual task...')
    response, content = h.request(uri=virtual_task_uri_interferers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_task_dict_interferers = json.loads(content)
    logging.debug(virtual_task_dict_interferers)
    
    # DEFINING VIRTUAL TASK 3 INSTALL IMAGE 3 ON VIRTUAL NODEGROUP 3
    
    virtual_task_dict_erase_interferers = {
        'name' : 'erase interferers node',
        'description' : DESCRIPTION,
        'step' : 5,
        'method' : 'DELETE',
        'target' : '%s/image' % (virtual_nodegroup_dict_interferers['uri'], )
    }
    
    logging.info('creating virtual task: erase virtual nodegroup interferers...')
    response, content = h.request(uri='%s/virtual-tasks/' % (experiment_dict['uri'], ), method='POST', body=json.dumps(virtual_task_dict_erase_interferers))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    virtual_task_uri_erase_interferers = response['content-location']
    logging.debug(virtual_task_uri_erase_interferers)
    
    logging.info('getting the created virtual task...')
    response, content = h.request(uri=virtual_task_uri_erase_interferers, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    virtual_task_dict_erase_interferers = json.loads(content)
    logging.debug(virtual_task_dict_erase_interferers)
    
    # GETTING THE UPDATED EXPERIMENT
    
    logging.info('getting the updated experiment...')
    response, content = h.request(uri=experiment_dict['uri'], method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    # CHECK THE EXPERIMENT RESOURCE
    
    logging.info('check the created experiment at %s' % (experiment_dict['uri'], ))

if __name__ == "__main__":
    main()
