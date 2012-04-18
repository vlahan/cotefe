# in this simple example we create 3 groups of nodes and we install 3 different images on them
import webbrowser
import logging
from cotefe.client import COTEFEAPI
from datetime import date, datetime, timedelta

# OAUTH2 CONFIGURATIONS

SERVER_URL = 'https://api.cotefe.net'
CLIENT_ID = 'e78507fb71e54a8281b3c676076e9158'
CLIENT_SECRET = '7ebc2f5e50904cef9df39926a50c2bec'
REDIRECT_URI = 'http://localhost'
ACCESS_TOKEN = 'bd5fb5eaa72c4788a1e96a2f720d45c8'

# SERVER_URL = 'http://localhost:8080'
# CLIENT_ID = '04e04ed1db97451497fa1e4ee14db358'
# CLIENT_SECRET = '7bf0545237c04509b15deca0612b3bb6'
# REDIRECT_URI = 'http://localhost'
# ACCESS_TOKEN = '406d80f0c88c4ebe927f1d595ec63db0'

# EXPERIMENT CONFIGURATION

DEFAULT_NAME = 'DEMO'
DEFAULT_DESCRIPTION = 'EWSN 2012 DEMO - PLEASE DO NOT DELETE!'
PLATFORM_NAME = 'TmoteSky'
# NUM_NODES_S = 1
# NUM_NODES_P = 93
# NUM_NODES_I = 2
NUM_NODES_S = 1
NUM_NODES_P = 3
NUM_NODES_I = 2
IMAGEFILE_S = 'images/demo_image_subscriber_ctp'
IMAGEFILE_P = 'images/demo_image_publishers_ctp'
IMAGEFILE_I = 'images/demo_image_interferers'

NUM_NODES_ALL = NUM_NODES_S + NUM_NODES_P + NUM_NODES_I

CALENDAR_SPAN_DAYS = 7
START_JOB_IN_MINUTES = 1
END_JOB_IN_MINUTES = 61

logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

try:
    
    access_token = ACCESS_TOKEN
    
except:
    
    unauthorized_api = COTEFEAPI(
        server_url = SERVER_URL,
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI)
    
    authorize_url = unauthorized_api.get_authorize_url()
    
    webbrowser.open(authorize_url)
    
    print "Visit this page and authorize access in your browser: ", authorize_url
    
    code = raw_input("Paste in code in query string after redirect: ").strip()
    
    access_token = unauthorized_api.exchange_code_for_access_token(code)
    
api = COTEFEAPI(server_url = SERVER_URL, access_token = access_token)    

logging.info('Your OAuth2 access_token is %s' % access_token)

me = api.get_current_user()

logging.info('Check your account information at %s' % me)


# CREATE A NEW PROJECT

my_project = api.create_project(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION)

logging.info('Check your project at %s' % my_project)

# CREATE A NEW EXPERIMENT

my_experiment = api.create_experiment(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    project = my_project)

logging.info('Check your experiment at %s' % my_experiment)

# SEARCH PLATFORM BY NAME

platform_result = api.search_platform(
    name = PLATFORM_NAME)

my_platform = platform_result[0]

logging.info('Check the platform "%s" at %s' % (PLATFORM_NAME, my_platform))

# CREATE A NEW PROPERTY SET

my_property_set = api.create_property_set(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    platform = my_platform,
    num_nodes = NUM_NODES_ALL,
    experiment = my_experiment)

logging.info('Check your property set at %s' % my_property_set)

# GET VIRTUAL NODES

my_virtual_nodes = api.get_virtual_nodes(
   experiment = my_experiment)

# CHECK NUMBER OF NODES

logging.info('%s virtual nodes retrieved.' % len(my_virtual_nodes))

assert len(my_virtual_nodes) == NUM_NODES_ALL

## SPLIT VIRTUAL NODES IN 3 GROUPS

my_virtual_nodes_S = my_virtual_nodes[0:NUM_NODES_S]
my_virtual_nodes_P = my_virtual_nodes[NUM_NODES_S:NUM_NODES_P+1]
my_virtual_nodes_I = my_virtual_nodes[NUM_NODES_P+1:]

## CHECK NUMBER OF NODES FOR EACH NODE GROUP

logging.debug('%s virtual nodes in group S.' % len(my_virtual_nodes_S))

assert len(my_virtual_nodes_S) == NUM_NODES_S

logging.debug('%s virtual nodes in group P.' % len(my_virtual_nodes_P))
assert len(my_virtual_nodes_P) == NUM_NODES_P

logging.debug('%s virtual nodes in group I.' % len(my_virtual_nodes_I))

assert len(my_virtual_nodes_I) == NUM_NODES_I

# CREATE A NEW VIRTUAL NODEGROUP WITH ALL NODES

my_virtual_nodegroup_ALL = api.create_virtual_nodegroup(
    name = 'All Nodes',
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_ALL.virtual_nodes) == NUM_NODES_ALL

logging.info('Check your virtual nodegroup ALL at %s' % my_virtual_nodegroup_ALL)

# CREATE A NEW VIRTUAL NODEGROUP S

my_virtual_nodegroup_S = api.create_virtual_nodegroup(
    name = 'Subscriber',
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_S,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == NUM_NODES_S

logging.info('Check your virtual nodegroup S at %s' % my_virtual_nodegroup_S)

# CREATE A NEW VIRTUAL NODEGROUP 2

my_virtual_nodegroup_P = api.create_virtual_nodegroup(
    name = 'Publishers',
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_P,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == NUM_NODES_S

logging.info('Check your virtual nodegroup P at %s' % my_virtual_nodegroup_P)

# CREATE A NEW VIRTUAL NODEGROUP 3

my_virtual_nodegroup_I = api.create_virtual_nodegroup(
    name = 'Interferers',
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_I,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == NUM_NODES_S

logging.info('Check your virtual nodegroup I at %s' % my_virtual_nodegroup_I)

# CREATE A NEW IMAGE 1

my_image_S = api.create_image(
    name = 'Image for Subscriber',
    description = DEFAULT_DESCRIPTION,
    imagefile = IMAGEFILE_S,
    experiment = my_experiment)
    
logging.info('Check your image S at %s' % my_image_S)

# CREATE A NEW IMAGE 2

my_image_P = api.create_image(
    name = 'Image for Publisher',
    description = DEFAULT_DESCRIPTION,
    imagefile = IMAGEFILE_P,
    experiment = my_experiment)
    
logging.info('Check your image P at %s' % my_image_P)

# CREATE A NEW IMAGE 3

my_image_I = api.create_image(
    name = 'Image for Interferer',
    description = DEFAULT_DESCRIPTION,
    imagefile = IMAGEFILE_I,
    experiment = my_experiment)
    
logging.info('Check your image I at %s' % my_image_I)

# CREATE A NEW VIRTUAL TASK 0

my_virtual_task_0 = api.create_virtual_task(
    name = 'Erase all nodes',
    description = DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_ALL,
    image = None,
    experiment = my_experiment)
    
logging.info('Check your virtual task 0 at %s' % my_virtual_task_0)

# CREATE A NEW VIRTUAL TASK 1

my_virtual_task_1 = api.create_virtual_task(
    name = 'Install image on Subscriber node',
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_S,
    image = my_image_S,
    experiment = my_experiment)
    
logging.info('Check your virtual task 1 at %s' % my_virtual_task_1)

# CREATE A NEW VIRTUAL TASK 2

my_virtual_task_2 = api.create_virtual_task(
    name = 'Install image on Publisher nodes',
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_P,
    image = my_image_P,
    experiment = my_experiment)

logging.info('Check your virtual task 2 at %s' % my_virtual_task_2)

# CREATE A NEW VIRTUAL TASK 3

my_virtual_task_3 = api.create_virtual_task(
    name = 'Install image on Interferer nodes',
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_I,
    image = my_image_I,
    experiment = my_experiment)
    
logging.info('Check your virtual task 3 at %s' % my_virtual_task_3)
   
# CREATE A NEW VIRTUAL TASK 4

my_virtual_task_4 = api.create_virtual_task(
    name = 'Erase Interferer nodes',
    description = DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_I,
    image = None,
    experiment = my_experiment)

logging.info('Check your virtual task 4 at %s' % my_virtual_task_4)

logging.info('Now check your experiment again at %s' % my_experiment)

exit()

# FIND TESTBEDS SUPPORTING THE EXPERIMENT

my_testbeds = api.search_testbed(
    support_experiment = my_experiment)

my_testbed = my_testbeds[0]

# FIND JOB CONFLICTING WITH THE CURRENT JOB IN THE SELECTED TESTBED

date_from = date.today()
date_to = date_from + timedelta(days = CALENDAR_SPAN_DAYS)


conflicting_jobs = api.search_job(
    for_experiment = my_experiment,
    testbed = my_testbed,
    date_from = date_from,
    date_to = date_to)

# try to schedule a job

my_job = api.create_job(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    datetime_from = datetime.utcnow() + timedelta(minutes = START_JOB_IN_MINUTES),
    datetime_to = datetime.utcnow() + timedelta(minutes = END_JOB_IN_MINUTES),
    experiment = my_experiment,
    testbed = my_testbed)

logging.info('Check your job at %s' % my_job)

# execute the job

api.execute(my_job)
