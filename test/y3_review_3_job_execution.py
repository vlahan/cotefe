import httplib2
import json
import logging
import sys
from datetime import date, datetime, timedelta
from utils import *

NODE_COUNT_VNG_1 = 10
NODE_COUNT_VNG_2 = 1
NODE_COUNT_TOT = NODE_COUNT_VNG_1 + NODE_COUNT_VNG_2

DESCRIPTION = 'CONET 3Y REVIEW TFA DEMO - PLEASE DO NOT DELETE'

def main():
    
    logging.basicConfig(
        level=logging.DEBUG,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )
    
    try:
        SERVER_URL = str(sys.argv[1])
        PLATFORM = str(sys.argv[2])
        N = int(sys.argv[3])
        # assert SERVER_URL in [ 'http://localhost:8080' , 'http://conet-testbed-federation.appspot.com' ]
        assert PLATFORM in [ 'TmoteSky' , 'eyesIFXv21' ]
    except Exception:
        print 'Usage: python %s SERVER_URL TmoteSky|eyesIFXv21 N' % __file__
        print 'Example: python %s https://conet-testbed-federation.appspot.com/ TmoteSky 10' % __file__
        sys.exit()

    h = httplib2.Http()
    
    logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    federation_dict = json.loads(content)
    logging.debug(federation_dict)
    
    # LIST OF TESTBEDS SUPPORTING THIS EXPERIMENT
    
    logging.info('getting the list of testbeds supporting this experiment (according to property_sets)...')
    response, content = h.request(uri='%s?supports_experiment=%s' % (federation_dict['testbeds'], experiment_dict['id']), method='GET', body='')
    assert response.status == 200
    logging.info('%d %s' % (response.status, response.reason))
    testbed_list = json.loads(content)
    logging.debug(testbed_list)
    
    logging.info('choosing the first testbed on the list (TWIST)...')
    testbed_dict = testbed_list[0]
    logging.info('selected testbed is %s' % testbed_list[0]['id'])
    
    exit()
    
    # GETTING THE LIST OF COLLIDING JOBS
    
    # dt_now = datetime.now()
    # dt_next_month = dt_now + timedelta(days=30)
    # str_now = berlin_datetime_to_utc_string(dt_now)
    # str_next_month = berlin_datetime_to_utc_string(dt_next_month)
    # logging.debug(str_now)
    # logging.debug(str_next_month)
    
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

if __name__ == "__main__":
    main()
