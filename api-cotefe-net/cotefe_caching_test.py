import webbrowser
import logging
import requests
from datetime import date, datetime, timedelta

SERVER_URL = 'http://localhost:8080'

ACCESS_TOKEN = '3a1a36bfe9e84f0a9908ab390667d4da'

DEFAULT_NAME = 'TEST'
DEFAULT_DESCRIPTION = 'COTEFE API TEST - PLEASE DO NOT DELETE!'

logging.basicConfig(
        level=logging.WARNING,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )


# # test begins # #

def apitest(method, url, headers, params, data, files, status_code_expected):
    
    r = requests.request(method=method, url=url, headers=headers, params=params, data=data, files=files, verify=False)
    logging.warning('%s %s ====> %s expected, %s received' % (method, url, status_code_expected, r.status_code))
    
# /

apitest(
    method = 'GET',
    url = SERVER_URL + '/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /me

apitest(
    method = 'GET',
    url = SERVER_URL + '/me',
    headers = { 'Authorization': 'OAuth %s' % ACCESS_TOKEN },
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /me/images/
# /me/experiments/
# /me/jobs/

# /users/

apitest(
    method = 'GET',
    url = SERVER_URL + '/users/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /users/ID
# /users/ID/images/
# /users/ID/experiments/
# /users/ID/jobs/

# /platforms/

apitest(
    method = 'GET',
    url = SERVER_URL + '/platforms/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /platforms/ID

# /interfaces/

apitest(
    method = 'GET',
    url = SERVER_URL + '/interfaces/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /interfaces/ID

# /sensors/

apitest(
    method = 'GET',
    url = SERVER_URL + '/sensors/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /sensors/ID

# /actuators/

apitest(
    method = 'GET',
    url = SERVER_URL + '/actuators/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /actuators/ID

# /testbeds/

apitest(
    method = 'GET',
    url = SERVER_URL + '/testbeds/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /testbeds/ID

# /images/

apitest(
    method = 'GET',
    url = SERVER_URL + '/images/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /images/ID

# /projects/

apitest(
    method = 'GET',
    url = SERVER_URL + '/projects/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /projects/ID

# /experiments/

apitest(
    method = 'GET',
    url = SERVER_URL + '/experiments/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /experiments/ID
# /experiments/ID/property-sets/
# /experiments/ID/property-sets/ID
# /experiments/ID/virtual-nodes/
# /experiments/ID/virtual-nodes/ID
# /experiments/ID/virtual-nodegroups/
# /experiments/ID/virtual-nodegroups/ID
# /experiments/ID/virtual-tasks/
# /experiments/ID/virtual-tasks/ID

# /jobs/

apitest(
    method = 'GET',
    url = SERVER_URL + '/jobs/',
    headers = {},
    params = {},
    data = {},
    files = {},
    status_code_expected = 200,
)

# /jobs/ID
# /jobs/ID/nodes/
# /jobs/ID/nodes/ID
# /jobs/ID/nodegroups/
# /jobs/ID/nodegroups/ID
# /jobs/ID/tasks/
# /jobs/ID/tasks/ID
# /jobs/ID/tasks/ID/run
# /jobs/ID/logs/
# /jobs/ID/logs/ID
# /jobs/ID/trace/
# /jobs/ID/trace/ID
