import httplib2
import json
import logging

ROOT_URL = 'http://localhost:8080/'
PLATFORM_ID = '4f93017c'
NODE_COUNT_TOT = 11
NODE_COUNT_VNG_1 = 10
NODE_COUNT_VNG_2 = 1


def main():

    h = httplib2.Http()
    
    logging.warning('getting the federation resource...')
    response, content = h.request(uri=ROOT_URL, method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    federation_dict = json.loads(content)
    logging.warning(federation_dict)
    
    project_dict = {
        'name' : 'sample project',
        'description' : 'PLEASE DO NOT DELETE',
    }
    
    logging.warning('creating a new project...')
    response, content = h.request(uri=federation_dict['projects'], method='POST', body=json.dumps(project_dict))
    assert response.status == 201
    logging.warning('%d %s' % (response.status, response.reason))
    project_uri = response['content-location']
    logging.warning(project_uri)
    
    logging.warning('getting the created project...')
    response, content = h.request(uri=response['content-location'], method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    project_dict = json.loads(content)
    logging.warning(project_dict)
    
    experiment_dict = {
        'name' : 'sample experiment',
        'description' : 'PLEASE DO NOT DELETE',
        'project' : project_dict['id']
    }
    
    logging.warning('creating a new experiment...')
    response, content = h.request(uri=federation_dict['experiments'], method='POST', body=json.dumps(experiment_dict))
    assert response.status == 201
    logging.warning('%d %s' % (response.status, response.reason))
    experiment_uri = response['content-location']
    logging.warning(project_dict)
    
    logging.warning('getting the created experiment...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.warning(experiment_dict)
    
    property_set_dict = {
        'name' : 'sample property set',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'platform' : PLATFORM_ID,
        'node_count' : NODE_COUNT_TOT
    }
    
    logging.warning('creating a new property set...')
    response, content = h.request(uri=federation_dict['property_sets'], method='POST', body=json.dumps(property_set_dict))
    assert response.status == 201
    logging.warning('%d %s' % (response.status, response.reason))
    property_set_uri = response['content-location']
    logging.warning(property_set_uri)
    
    logging.warning('getting the created property set (including the created virtual nodes)...')
    response, content = h.request(uri=property_set_uri, method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    property_set_dict = json.loads(content)
    logging.warning(property_set_dict)
    
    logging.warning('getting the updated experiment (including virtual nodes)...')
    response, content = h.request(uri=experiment_uri, method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    experiment_dict = json.loads(content)
    logging.warning(experiment_dict)
    
    logging.warning('getting the first %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri='%s?experiment=%s&n=%d' % (federation_dict['virtual_nodes'], experiment_dict['id'], NODE_COUNT_VNG_1), method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    virtual_node_list_1 = json.loads(content)
    logging.warning(virtual_node_list_1)
    
    virtual_node_id_list_1 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_1 ]
    assert len(virtual_node_id_list_1) == NODE_COUNT_VNG_1
    
    virtual_nodegroup_dict_1 = {
        'name' : 'publishers',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_1
    }
    
    logging.warning('creating a virtual nodegroup out of %d virtual nodes...' % (NODE_COUNT_VNG_1))
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_1))
    assert response.status == 201
    logging.warning('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_1 = response['content-location']
    logging.warning(virtual_nodegroup_uri_1)
    
    logging.warning('getting the remaining virtual node...')
    response, content = h.request(uri='%s?experiment=%s&name=%s' % (federation_dict['virtual_nodes'], experiment_dict['id'], 'virtual_node_11'), method='GET', body='')
    assert response.status == 200
    logging.warning('%d %s' % (response.status, response.reason))
    virtual_node_list_2 = json.loads(content)
    logging.warning(virtual_node_list_2)
    
    virtual_node_id_list_2 = [ json.loads(h.request(uri=virtual_node_dict['uri'], method='GET', body='')[1])['id'] for virtual_node_dict in virtual_node_list_2 ]
    assert len(virtual_node_id_list_2) == NODE_COUNT_VNG_2
    
    virtual_nodegroup_dict_2 = {
        'name' : 'subscriber',
        'description' : 'PLEASE DO NOT DELETE',
        'experiment' : experiment_dict['id'],
        'virtual_nodes' : virtual_node_id_list_2
    }
    
    logging.warning('creating a virtual nodegroup out with one virtual node...')
    response, content = h.request(uri=federation_dict['virtual_nodegroups'], method='POST', body=json.dumps(virtual_nodegroup_dict_2))
    assert response.status == 201
    logging.warning('%d %s' % (response.status, response.reason))
    virtual_nodegroup_uri_2 = response['content-location']
    logging.warning(virtual_nodegroup_uri_2)

if __name__ == "__main__":
    main()
