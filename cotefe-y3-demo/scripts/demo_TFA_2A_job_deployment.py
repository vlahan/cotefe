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
    
    JOB = raw_input('Job URI: ')
    
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    
    # logging.info('getting the federation resource...')
    response, content = h.request(uri=SERVER_URL, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    federation_dict = json.loads(content)
    logging.debug(federation_dict)
    
    # GETTING THE JOB
    
    logging.info('getting the job resource at %s...' % (JOB, ))
    response, content = h.request(uri=JOB, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    job_dict = json.loads(content)
    logging.debug(job_dict)
    
    # LIST OF TASKS 
    
    uri='%s/tasks/' % (job_dict['uri'], )
    logging.debug(uri)
    logging.info('getting the list of tasks at %s...' % (uri, ))
    response, content = h.request(uri=uri, method='GET', body='')
    logging.info('%d %s' % (response.status, response.reason))
    assert response.status == 200
    task_list = json.loads(content)
    logging.debug(task_list)
    
    # logging.info('!!!!!!READY TO EXECUTE %d TASKS!!!!!!' % (len(task_list, )))
    logging.info('!!!!!!READY TO DEPLOY THE EXPERIMENT!!!!!!')
    
    for task_dict in task_list:
        
        if task_dict['step']<4:
            
            raw_input('press ENTER when you want to execute the next task...')
            uri='%s/run' % (task_dict['uri'], )
            logging.debug(uri)
            logging.info('executing the task at %s...' % (uri, ))
            headers = {'Content-Length' : '0'}
            response, content = h.request(uri=uri, method='PUT', body='', headers=headers)
            logging.info('check the status of this request at %s' % (response['location'], ))
            logging.info('%d %s' % (response.status, response.reason))
    
    logging.info('CONGRATULATIONS! JOB COMPLETED!')

if __name__ == "__main__":
    main()
