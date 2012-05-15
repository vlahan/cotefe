import webbrowser
import logging
import requests
from datetime import date, datetime, timedelta

# SERVER_URL = 'https://www.twist.tu-berlin.de:8001'
SERVER_URL = 'http://localhost:8001'

DEFAULT_NAME = 'TEST'
DEFAULT_DESCRIPTION = 'TESTBED ABSTRACTION API TEST - PLEASE DO NOT DELETE!'

logging.basicConfig(
        level=logging.WARNING,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

def apitest(method, url, headers, params, data, files, status_code_expected):
    
    r = requests.request(method=method, url=url, headers=headers, params=params, data=data, files=files, verify=False)
    logging.warning('%s %s ====> %s expected, %s received' % (method, url, status_code_expected, r.status_code))

# # test begins # #

apitest(
    method = 'GET',
    url = SERVER_URL + '/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/platforms/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/interfaces/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/sensors/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/actuators/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/images/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

apitest(
    method = 'GET',
    url = SERVER_URL + '/jobs/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)


