import httplib2
import json
import logging
import sys

DESCRIPTION = 'CONET 3Y REVIEW DEMO - PLEASE DO NOT DELETE'

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z',
    )
    
    try:
        SERVER_URL = sys.argv[1]
        PLATFORM = sys.argv[2]
        assert PLATFORM in [ 'tmotesky' , 'eyesIFXv21' ]
        NODE_COUNT_VNG_1 = int(sys.argv[3])
        NODE_COUNT_VNG_2 = int(sys.argv[4])
        NODE_COUNT_TOT = NODE_COUNT_VNG_1 + NODE_COUNT_VNG_2
    except Exception:
        print 'Usage: python %s SERVER_URL tmotesky|eyesIFXv21 N_NODES_VNG_1 N_NODES_VNG_2' % __file__
        print 'Example: python %s https://conet-testbed-federation.appspot.com/ tmotesky 100 1' % __file__
        sys.exit()

    h = httplib2.Http()
    
    logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    federation_dict = json.loads(content)
    logging.debug(federation_dict)
    
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
    
    logging.info('getting the a list a list of platforms filtering by name \"%s\"...' % PLATFORM)
    response, content = h.request(uri='%s?name=%s' % (federation_dict['platforms'], PLATFORM), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_list = json.loads(content)
    logging.debug(platform_list)
    
    logging.info('getting the platform with name \"%s\"...' % PLATFORM)
    response, content = h.request(uri=platform_list[0]['uri'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_dict = json.loads(content)
    logging.debug(platform_dict)
    
    property_set_dict = {
        'name' : 'sample property set',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'platform' : platform_dict['id'],
        'node_count' : NODE_COUNT_TOT
    }
    
    logging.info('creating a new property set...')
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
    
    logging.info('getting the updated experiment (including virtual nodes)...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.debug(experiment_dict)
    
    logging.info('getting the first %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri='%s?experiment=%s&n=%d' % (federation_dict['virtual_nodes'], experiment_dict['id'], NODE_COUNT_VNG_1), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_node_list_1 = json.loads(content)
    logging.debug(virtual_node_list_1)
    
    virtual_node_id_list_1 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_1 ]
    assert len(virtual_node_id_list_1) == NODE_COUNT_VNG_1
    
    virtual_nodegroup_dict_1 = {
        'name' : 'publishers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_1
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_1))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_1 = response['content-location']
    logging.debug(virtual_nodegroup_uri_1)
    
    logging.info('getting the virtual nodegroup 1...')
    response, content = h.request(uri=virtual_nodegroup_uri_1, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_1 = json.loads(content)
    logging.debug(virtual_nodegroup_dict_1)
    
    logging.info('getting the remaining virtual node...')
    response, content = h.request(uri='%s?experiment=%s&name=%s' % (federation_dict['virtual_nodes'], experiment_dict['id'], 'virtual_node_11'), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_node_list_2 = json.loads(content)
    logging.debug(virtual_node_list_2)
    
    virtual_node_id_list_2 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_2 ]
    assert len(virtual_node_id_list_2) == NODE_COUNT_VNG_2
    
    virtual_nodegroup_dict_2 = {
        'name' : 'subscriber',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_2
    }
    
    logging.info('creating a virtual nodegroup out with one virtual node...')
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_2))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_2 = response['content-location']
    logging.debug(virtual_nodegroup_uri_2)
    
    logging.info('getting the virtual nodegroup 2...')
    response, content = h.request(uri=virtual_nodegroup_uri_2, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_2= json.loads(content)
    logging.debug(virtual_nodegroup_dict_2)
    
    image_1 = {
        'name' : 'image for publishers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id']
    }
    
    logging.info('uploading image 1...')
    response, content = h.request(uri=federation_dict['images'], method='POST', body=json.dumps(image_1))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_1 = response['content-location']
    logging.debug(image_uri_1)
    
    logging.info('getting image 1...')
    response, content = h.request(uri=image_uri_1, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_1 = json.loads(content)
    logging.debug(image_dict_1)
    
    image_2 = {
        'name' : 'image for subscribers',
        'description' : DESCRIPTION,
        'experiment' : experiment_dict['id']
    }
    
    logging.info('uploading image 2...')
    response, content = h.request(uri=federation_dict['images'], method='POST', body=json.dumps(image_2))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    image_uri_2 = response['content-location']
    logging.debug(image_uri_2)
    
    logging.info('getting image 2...')
    response, content = h.request(uri=image_uri_2, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    image_dict_2 = json.loads(content)
    logging.debug(image_dict_2)
    
    logging.info('installing image 1 on virtual nodegroup 1...')
    response, content = h.request(uri='%s%s/image/%s' % (federation_dict['virtual_nodegroups'], virtual_nodegroup_dict_1['id'], image_dict_1['id']), method='PUT', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    logging.info('installing image 2 on virtual nodegroup 2...')
    response, content = h.request(uri='%s%s/image/%s' % (federation_dict['virtual_nodegroups'], virtual_nodegroup_dict_2['id'], image_dict_2['id']), method='PUT', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    
    # CLEANING UP THINGS
    # CASCADE DELETE DOES NOT WORK ON GAE!!!!!!!!!
    #logging.info('deleting the project and all its children... CASCADE DELETE DOES NOT WORK ON GAE!!!!!!!!!')
    #response, content = h.request(uri=project_uri, method='DELETE', body='')
    #assert response.status == 200
    #logging.info('%d %s' % (response.status, response.reason))

if __name__ == "__main__":
    main()
