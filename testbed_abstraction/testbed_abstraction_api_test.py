import webbrowser
import logging
import requests
from datetime import date, datetime, timedelta

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = '8001'

SERVER_URL = 'http://' + SERVER_ADDRESS + ':' + SERVER_PORT

DEFAULT_RESOURCE_NAME = 'TEST RESOURCE'
DEFAULT_RESOURCE_DESCRIPTION = 'TESTBED ABSTRACTION API TEST - PLEASE DO NOT DELETE!'
DEFAULT_PLATFORM_ID = 'tmotesky'
DEFAULT_N = '10'
DEFAULT_NODE_ID = 'ABCDEFGHI'
DEFAULT_DATETIME_FROM = 'YYYY-MM-DDThh:mm:ss'
DEFAULT_DATETIME_TO = 'YYYY-MM-DDThh:mm:ss'
DEFAULT_JOB_ID = '123'

logging.basicConfig(
        level=logging.WARNING,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

def apitest(method, url, headers, params, data, files, status_code_expected):
    
    response = requests.request(method=method, url=url, headers=headers, params=params, data=data, files=files, verify=False)
    logging.warning('%s %s ====> %s expected, %s received' % (method, url, status_code_expected, response.status_code))
    
    return response

# # test begins # #

# getting the testbed information
apitest(
    method = 'GET',
    url = SERVER_URL + '/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the list of nodes
apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the list of nodes of a given platform
apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/',
    headers = {},
    params = { 'platform' : DEFAULT_PLATFORM_ID },
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the list of N nodes
apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/',
    headers = {},
    params = {  },
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the list of N nodes of platform PLATFORM_ID
apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/',
    headers = {},
    params = { 'platform' : DEFAULT_PLATFORM_ID, 'n' : DEFAULT_N },
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the details about a specific node
apitest(
    method = 'GET',
    url = SERVER_URL + '/nodes/' + DEFAULT_NODE_ID,
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# getting the list of reservations / scheduled jobs
apitest(
    method = 'GET',
    url = SERVER_URL + '/jobs/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# creating a new job
apitest(
    method = 'POST',
    url = SERVER_URL + '/jobs/',
    headers = {},
    params = {},
    data = {
        'name' : DEFAULT_RESOURCE_NAME,
        'description' : DEFAULT_RESOURCE_DESCRIPTION,
        'datetime_from' : DEFAULT_DATETIME_FROM,
        'datetime_to' : DEFAULT_DATETIME_TO,
        "nodes" : [ DEFAULT_NODE_ID ]
    },
    files = {},
    status_code_expected = 201,
)

# getting details about a specific job
apitest(
    method = 'GET',
    url = SERVER_URL + '/jobs/' + DEFAULT_JOB_ID,
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# editing a job
apitest(
    method = 'PUT',
    url = SERVER_URL + '/jobs/' + DEFAULT_JOB_ID,
    headers = {},
    params = {},
    data = {
        'name' : 'I HAVE CHANGED THIS',
        'description' : 'I HAVE CHANGED THIS',
        'datetime_from' : DEFAULT_DATETIME_FROM,
        'datetime_to' : DEFAULT_DATETIME_TO,
        "nodes" : [ DEFAULT_NODE_ID ]
    },
    files = {},
    status_code_expected = 200,
)

# deleting a given job
apitest(
    method = 'DELETE',
    url = SERVER_URL + '/jobs/' + DEFAULT_JOB_ID,
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

