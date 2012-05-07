import requests

TESTBED_SERVER = 'http://localhost:8001/'

r = requests.get(TESTBED_SERVER)

assert r.status_code == 200