import httplib2
import json
import logging
import sys

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    try:
        SERVER_URL = str(sys.argv[1])
    except Exception:
        print 'Usage: python %s SERVER_URL' % __file__
        print 'Example: python %s https://www.twist.tu-berlin.de:8001' % __file__
        sys.exit()

    h = httplib2.Http()
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)

    logging.info('getting the list of platforms...')
    response, content = h.request(uri=testbed_dict['platforms'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_list = json.loads(content)
    logging.debug(platform_list)
    platform_id_list = [p['id'] for p in platform_list]
    logging.info('list of platform ids %s' % platform_id_list)
    
    logging.info('getting the list of nodes...')
    response, content = h.request(uri=testbed_dict['nodes'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list = json.loads(content)
    logging.debug(node_list)
    node_total_count = len(node_list)
    logging.info('%d nodes received in total' % node_total_count)
    
    node_count = 0
    
    for platform in platform_id_list:
        logging.info('getting the list of nodes with platform %s...' % platform)
        response, content = h.request(uri='%s?platform=%s' % (testbed_dict['nodes'], platform), method='GET', body='')
        assert response.status == 200
        logging.info('%d %s' % (response.status, response.reason))
        node_list = json.loads(content)
        logging.debug(node_list)
        logging.info('%d nodes received with platform %s' % (len(node_list), platform))
        node_count += len(node_list)
    
    assert node_count == node_total_count
    logging.info('the total sum of nodes is equal to the sum of nodes per platform')

if __name__ == "__main__":
    main()
