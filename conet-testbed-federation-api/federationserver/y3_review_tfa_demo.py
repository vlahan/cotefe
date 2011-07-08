import httplib2
import json
import logging

SERVER_URL = 'http://localhost:8080/'
# SERVER_URL = 'https://conet-testbed-federation.appspot.com/'
PLATFORM_NAME = 'tmotesky'
NODE_COUNT_TOT = 11
NODE_COUNT_VNG_1 = 10
NODE_COUNT_VNG_2 = 1

def main():

    h = httplib2.Http()
    
    logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    federation_dict = json.loads(content)
    logging.info(federation_dict)
    
    
    
    project_dict = {
        'name' : 'sample project',
        'description' : 'PLEASE DO NOT DELETE',
    }
    
    logging.info('creating a new project...')
    response, content = h.request(uri=federation_dict['projects'], method='POST', body=json.dumps(project_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    project_uri = response['content-location']
    logging.info(project_uri)
    
    logging.info('getting the created project...')
    response, content = h.request(uri=response['content-location'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    project_dict = json.loads(content)
    logging.info(project_dict)
    
    experiment_dict = {
        'name' : 'sample experiment',
        'description' : 'PLEASE DO NOT DELETE',
        'project' : project_dict['id']
    }
    
    logging.info('creating a new experiment...')
    response, content = h.request(uri=federation_dict['experiments'], method='POST', body=json.dumps(experiment_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    experiment_uri = response['content-location']
    logging.info(project_dict)
    
    logging.info('getting the created experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.info(experiment_dict)
    
    logging.info('getting the a list a list of platforms filtering by name \"%s\"...' % PLATFORM_NAME)
    response, content = h.request(uri='%s?name=%s' % (federation_dict['platforms'], PLATFORM_NAME), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_list = json.loads(content)
    logging.info(platform_list)
    
    logging.info('getting the platform with name \"%s\"...' % PLATFORM_NAME)
    response, content = h.request(uri=platform_list[0]['uri'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_dict = json.loads(content)
    logging.info(platform_dict)
    
    property_set_dict = {
        'name' : 'sample property set',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'platform' : platform_dict['id'],
        'node_count' : NODE_COUNT_TOT
    }
    
    logging.info('creating a new property set...')
    response, content = h.request(uri=federation_dict['property_sets'], method='POST', body=json.dumps(property_set_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    property_set_uri = response['content-location']
    logging.info(property_set_uri)
    
    logging.info('getting the created property set (including the created virtual nodes)...')
    response, content = h.request(uri=property_set_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    property_set_dict = json.loads(content)
    logging.info(property_set_dict)
    
    logging.info('getting the updated experiment (including virtual nodes)...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.info(experiment_dict)
    
    logging.info('getting the first %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri='%s?experiment=%s&n=%d' % (federation_dict['virtual_nodes'], experiment_dict['id'], NODE_COUNT_VNG_1), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_node_list_1 = json.loads(content)
    logging.info(virtual_node_list_1)
    
    virtual_node_id_list_1 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_1 ]
    assert len(virtual_node_id_list_1) == NODE_COUNT_VNG_1
    
    virtual_nodegroup_dict_1 = {
        'name' : 'publishers',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_1
    }
    
    logging.info('creating a virtual nodegroup out of %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_1))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_1 = response['content-location']
    logging.info(virtual_nodegroup_uri_1)
    
    logging.info('getting the virtual nodegroup 1...')
    response, content = h.request(uri=virtual_nodegroup_uri_1, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_1 = json.loads(content)
    logging.info(virtual_nodegroup_dict_1)
    
    logging.info('getting the remaining virtual node...')
    response, content = h.request(uri='%s?experiment=%s&name=%s' % (federation_dict['virtual_nodes'], experiment_dict['id'], 'virtual_node_11'), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_node_list_2 = json.loads(content)
    logging.info(virtual_node_list_2)
    
    virtual_node_id_list_2 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_2 ]
    assert len(virtual_node_id_list_2) == NODE_COUNT_VNG_2
    
    virtual_nodegroup_dict_2 = {
        'name' : 'subscriber',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_2
    }
    
    logging.info('creating a virtual nodegroup out with one virtual node...')
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_2))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_2 = response['content-location']
    logging.info(virtual_nodegroup_uri_2)
    
    logging.info('getting the virtual nodegroup 2...')
    response, content = h.request(uri=virtual_nodegroup_uri_2, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    virtual_nodegroup_dict_2= json.loads(content)
    logging.info(virtual_nodegroup_dict_2)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %z',
    )
    main()
