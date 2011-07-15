import httplib2
import json
import logging
import sys
from datetime import datetime, timedelta, date
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import pytz

# UTC time zone
utc = pytz.utc

# Europe/Berlin time zone
berlin = pytz.timezone('Europe/Berlin')

# datetime string formats
FMT_DT_TO_STR = '%Y-%m-%dT%H:%M:%S%z'
FMT_STR_TO_DT = '%Y-%m-%dT%H:%M:%S+0000'

def berlin_datetime_to_berlin_string(dt):
    dt_berlin = berlin.localize(dt)
    return dt_berlin.strftime(FMT_DT_TO_STR)

def utc_datetime_to_utc_string(dt):
    dt_utc = utc.localize(dt)
    return dt_utc.strftime(FMT_DT_TO_STR)

def berlin_datetime_to_utc_string(dt):
    dt_berlin = berlin.localize(dt)
    dt_utc = dt_berlin.astimezone(utc)
    return dt_utc.strftime(FMT_DT_TO_STR)

def naive_string_to_utc_datetime(dt_str):
    return berlin.localize(datetime.strptime(dt_str, FMT_STR_TO_DT))

def utc_string_to_utc_datetime(dt_str):
    return datetime.strptime(dt_str, FMT_STR_TO_DT)

def get_dt_now_utc():
    dt_now_berlin = berlin.localize(datetime.now())
    dt_now_utc = dt_now_berlin.astimezone(utc)
    return dt_now_utc

def main():
    
    logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    # SERVER_URL = 'https://www.twist.tu-berlin.de:8001'
    SERVER_URL = 'http://localhost:8001'
    CALENDAR_SPAN_IN_DAYS = 7
    DESCRIPTION = 'CONET 3Y REVIEW DEMO - PLEASE DO NOT DELETE'
    PLATFORM = 'TmoteSky'
    N = 102
        
    assert PLATFORM in [ 'TmoteSky' , 'eyesIFXv21' ]

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
    
    date_from = date.today()
    date_to = date_from + timedelta(days=CALENDAR_SPAN_IN_DAYS)
            
    logging.info('getting a list of all jobs between date %s and date %s...' % (date_from, date_to))
    response, content = h.request(uri='%s?date_from=%s&date_to=%s' % (testbed_dict['jobs'], date_from, date_to), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    job_list = json.loads(content)
    logging.debug(job_list)
    logging.info('%d jobs returned' % len(job_list))
    
    datetime_from = datetime.now() + timedelta(minutes=2)
    datetime_to = datetime.now() + timedelta(minutes=12)
    
    str_from = berlin_datetime_to_utc_string(datetime_from)
    str_to = berlin_datetime_to_utc_string(datetime_to)
    
    job_dict = {
        'name' : 'sample job',
        'description' : DESCRIPTION,
        'nodes' : [ n['id'] for n in node_list ],
        'datetime_from' : str_from,
        'datetime_to' : str_to,
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
