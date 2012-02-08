import httplib2
import json
import logging
import sys
from datetime import date, datetime, timedelta
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
    
    SERVER_URL = 'http://api.cotefe.net'
    # SERVER_URL = 'http://localhost:8080'
    
    EXPERIMENT = raw_input('Experiment URI: ')
    
    PLATFORM = 'TmoteSky'
    
    START_JOB_IN_MINUTES = 1
    END_JOB_IN_MINUTES = 1665
    
    CALENDAR_SPAN_IN_DAYS = 7

    DESCRIPTION = 'TWIST RESTful API DEMO - PLEASE DO NOT DELETE!'
    SUBSCRIBER = 1
    PUBLISHERS = 93
    INTERFERERS = 2
    
    N = SUBSCRIBER + PUBLISHERS + INTERFERERS

    h = httplib2.Http()
    
    logging.info('getting the federation resource...')
    response, content =  h.request(uri=SERVER_URL, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    federation_dict = json.loads(content)
    # logging.debug(federation_dict)
    
    # GETTING THE EXPERIMENT
    
    logging.info('getting the experiment resource at %s...' % (EXPERIMENT, ))
    response, content = h.request(uri=EXPERIMENT, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    experiment_dict = json.loads(content)
    # logging.debug(experiment_dict)
    
    # LIST OF TESTBEDS SUPPORTING THIS EXPERIMENT
    
    logging.info('getting the list of testbeds supporting this experiment (according to property_sets)...')
    uri='%s?supports_experiment=%s' % (federation_dict['testbeds'], experiment_dict['id'])
    logging.debug(uri)
    response, content = h.request(uri=uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    testbed_list = json.loads(content)
    logging.debug(testbed_list)
    
    logging.info('choosing the first testbed on the list (TWIST)...')
    testbed_dict = testbed_list[0]
    logging.info('selected testbed is %s' % testbed_list[0]['id'])
    
    # GETTING THE CALENDAR
    
    date_from = date.today()
    date_to = date_from + timedelta(days=CALENDAR_SPAN_IN_DAYS)
            
    logging.info('getting a list of all jobs between date %s and date %s...' % (date_from, date_to))
    uri='%s?for_experiment=%s&testbed=%s&date_from=%s&date_to=%s' % (federation_dict['jobs'], experiment_dict['id'], testbed_dict['id'], date_from, date_to)
    logging.debug(uri)
    response, content = h.request(uri=uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    job_list = json.loads(content)
    logging.debug(job_list)
    logging.info('%d jobs returned' % len(job_list))
    
    # TRY TO SCHEDULE A JOB
    
    job_dict = {
        'name' : 'sample job',
        'description' : DESCRIPTION,
        'datetime_from' : berlin_datetime_to_utc_string(datetime.now() + timedelta(minutes=START_JOB_IN_MINUTES)),
        'datetime_to' : berlin_datetime_to_utc_string(datetime.now() + timedelta(minutes=END_JOB_IN_MINUTES)),
        'experiment' : experiment_dict['id'],
        'testbed' : testbed_dict['id']
    }
    
    logging.debug(job_dict)
    
    logging.info('trying to schedule a job for this experiment in testbed %s' % (testbed_dict['id'], ))
    response, content = h.request(uri=federation_dict['jobs'], method='POST', body=json.dumps(job_dict))
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 201
    job_uri = response['content-location']
    logging.debug(job_uri)
    
    logging.info('getting the job...')
    response, content = h.request(uri=job_uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    job_dict = json.loads(content)
    logging.debug(job_dict)
    
    logging.info('check the created job at %s' % (job_dict['uri'], ))
    
if __name__ == "__main__":
    main()
