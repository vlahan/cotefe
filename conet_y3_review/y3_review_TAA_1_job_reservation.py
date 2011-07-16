import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import pytz

def berlin_datetime_to_utc_string(dt):
    FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S%z'
    utc = pytz.utc
    berlin = pytz.timezone('Europe/Berlin')
    dt_berlin = berlin.localize(dt)
    dt_utc = dt_berlin.astimezone(utc)
    return dt_utc.strftime(FMT_DT_TO_STR)

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
#    SERVER_URL = str(sys.argv[1]) or 'https://www.twist.tu-berlin.de:8001/'
#    PLATFORM = str(sys.argv[2]) or 'TmoteSky'
#    N = int(sys.argv[3]) or 96
#    START_JOB_IN_MINUTES = int(sys.argv[4]) or 1
#    END_JOB_IN_MINUTES = int(sys.argv[5]) or 31
    
    SERVER_URL = 'https://www.twist.tu-berlin.de:8001/'
    PLATFORM = 'TmoteSky'
    N = 96
    START_JOB_IN_MINUTES = 1
    END_JOB_IN_MINUTES = 31
    
    CALENDAR_SPAN_IN_DAYS = 7
    DESCRIPTION = 'CONET 3Y REVIEW DEMO - PLEASE DO NOT DELETE'
    
    assert PLATFORM in [ 'TmoteSky' , 'eyesIFXv20', 'eyesIFXv21' ]

    h = httplib2.Http()
    
    logging.info('getting the testbed resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_dict = json.loads(content)
    logging.debug(testbed_dict)

    logging.info('getting the list of provided node platforms...')
    response, content = h.request(uri=testbed_dict['platforms'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    platform_list = json.loads(content)
    logging.debug(platform_list)
    platform_id_list = [p['id'] for p in platform_list]
    logging.info('list of platform ids %s' % platform_id_list)
    
    logging.info('getting all available testbed nodes...')
    response, content = h.request(uri=testbed_dict['nodes'], method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list = json.loads(content)
    logging.debug(node_list)
    node_total_count = len(node_list)
    logging.info('%d nodes received in total' % node_total_count)
    
    logging.info('exploring %s...' % (testbed_dict['id']))
    
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
    logging.debug('the total sum of nodes is equal to the sum of nodes per platform')
    
    logging.info('getting a list of %d of nodes with platform %s...' % (N, PLATFORM))
    response, content = h.request(uri='%s?platform=%s&n=%d' % (testbed_dict['nodes'], PLATFORM, N), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    node_list = json.loads(content)
    logging.debug(node_list)
    if len(node_list) == N:
        logging.info('OK! %d nodes found with platform %s' % (len(node_list), PLATFORM))
        r = raw_input('Do you want to reserve a job? (Y/N) ')
        if r != 'Y':
            exit()
    else:
        logging.info('OUCH! you asked for %d nodes with platform %s but you only received %d' % (N, PLATFORM, len(node_list)))
        r = raw_input('Do you still want to go on with %d nodes? (Y/N) ' % len(node_list))
        if r != 'Y':
            exit()
            
    # GETTING THE CALENDAR
    
    date_from = date.today()
    date_to = date_from + timedelta(days=CALENDAR_SPAN_IN_DAYS)
            
    logging.info('getting a list of all jobs between date %s and date %s...' % (date_from, date_to))
    response, content = h.request(uri='%s?date_from=%s&date_to=%s' % (testbed_dict['jobs'], date_from, date_to), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_list = json.loads(content)
    logging.debug(job_list)
    logging.info('%d jobs returned' % len(job_list))
    
    # CREATING A JOB
    
    job_dict = {
        'name' : 'sample job',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list ],
        'datetime_from' : berlin_datetime_to_utc_string(datetime.now() + timedelta(minutes=START_JOB_IN_MINUTES)),
        'datetime_to' : berlin_datetime_to_utc_string(datetime.now() + timedelta(minutes=END_JOB_IN_MINUTES)),
    }
    
    logging.debug(job_dict)
    
    logging.info('creating a new job..')    
    response, content = h.request(uri=testbed_dict['jobs'], method='POST', body=json.dumps(job_dict))
    assert response.status == 201
    logging.info('%d %s' % (response.status, response.reason))
    job_uri = response['content-location']
    logging.info(job_uri)
    
    logging.info('getting the job...')
    response, content = h.request(uri=job_uri, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_dict = json.loads(content)
    logging.debug(job_dict)
    
    logging.info('check the created job including its subresrouces at %s' % (job_dict['uri'], ))
    
if __name__ == "__main__":
    main()
