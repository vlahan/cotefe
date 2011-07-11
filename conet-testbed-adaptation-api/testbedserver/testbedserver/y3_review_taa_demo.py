import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    try:
        SERVER_URL = str(sys.argv[1])
        PLATFORM = str(sys.argv[2])
        N = int(sys.argv[3])
        assert PLATFORM in [ 'TmoteSky' , 'eyesIFXv21' ]
    except Exception:
        print 'Usage: python %s SERVER_URL' % __file__
        print 'Example: python %s https://www.twist.tu-berlin.de:8001 TmoteSky 10' % __file__
        sys.exit()

    h = httplib2.Http()
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)

#    logging.info('getting the list of platforms...')
#    response, content = h.request(uri=testbed_dict['platforms'], method='GET', body='')
#    assert response.status == 200
#    logging.info('%d %s' % (response.status, response.reason))
#    platform_list = json.loads(content)
#    logging.debug(platform_list)
#    platform_id_list = [p['id'] for p in platform_list]
#    logging.info('list of platform ids %s' % platform_id_list)
#    
#    logging.info('getting the list of nodes...')
#    response, content = h.request(uri=testbed_dict['nodes'], method='GET', body='')
#    assert response.status == 200
#    logging.info('%d %s' % (response.status, response.reason))
#    node_list = json.loads(content)
#    logging.debug(node_list)
#    node_total_count = len(node_list)
#    logging.info('%d nodes received in total' % node_total_count)
#    
#    node_count = 0
#    
#    for platform in platform_id_list:
#        logging.info('getting the list of nodes with platform %s...' % platform)
#        response, content = h.request(uri='%s?platform=%s' % (testbed_dict['nodes'], platform), method='GET', body='')
#        assert response.status == 200
#        logging.info('%d %s' % (response.status, response.reason))
#        node_list = json.loads(content)
#        logging.debug(node_list)
#        logging.info('%d nodes received with platform %s' % (len(node_list), platform))
#        node_count += len(node_list)
#    
#    assert node_count == node_total_count
#    logging.info('the total sum of nodes is equal to the sum of nodes per platform')
    
    logging.info('getting a list of %d of nodes with platform %s...' % (N, PLATFORM))
    response, content = h.request(uri='%s?platform=%s&n=%d' % (testbed_dict['nodes'], PLATFORM, N), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list = json.loads(content)
    logging.debug(node_list)
    if len(node_list) == N:
        logging.info('OK! %d nodes found with platform %s' % (len(node_list), PLATFORM))
    else:
        logging.info('OUCH! you asked for %d nodes with platform %s but you only received %d' % (N, PLATFORM, len(node_list)))
        r = raw_input('Do you still want to go on with %d nodes? (Y/N) ' % len(node_list))
        if r == 'Y':
            N = len(node_list)
        else:
            exit()
    
    d_from = date.today()
    d_to = d_from + timedelta(days=2)
            
    logging.info('getting a list of all jobs between date %s and date %s...' % (d_from, d_to))
    response, content = h.request(uri='%s?date_from=%s&date_to=%s' % (testbed_dict['jobs'], d_from, d_to), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_list = json.loads(content)
    logging.debug(job_list)
    logging.info('%d jobs returned' % len(job_list))
    
    exit()
    
    logging.info('creating a new job..')    
    response, content = h.request(uri=testbed_dict['jobs'], method='POST', body=json.dumps(project_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    project_uri = response['content-location']
    logging.debug(project_uri)
       
if __name__ == "__main__":
    main()
