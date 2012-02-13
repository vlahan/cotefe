# in this simple example we create 3 groups of nodes and we install 3 different images on them
import webbrowser
import logging
from cotefe.client import COTEFEAPI

# OAUTH2 CONFIGURATIONS

# SERVER_URL = 'https://api.cotefe.net'
# CLIENT_ID = 'd770617a49f54c0cbb0dc12175a6cbae'
# CLIENT_SECRET = '565af7fd385644de88c326dcb7c499f6'
# REDIRECT_URI = 'http://localhost'
# ACCESS_TOKEN = '4f1664a88ca0400eab78fa8a575cbfba'

SERVER_URL = 'http://localhost:8080'
CLIENT_ID = '600803dc3d2547f3bacded2fd90c61f7'
CLIENT_SECRET = 'bfdca3017e324028a3ba992cc61dcfc8'
REDIRECT_URI = 'http://localhost'
ACCESS_TOKEN = '7e49782bb6f244099026b5a264453c92'

# EXPERIMENT CONFIGURATION

DEFAULT_NAME = 'DEMO'
DEFAULT_DESCRIPTION = 'COTEFE API DEMO - PLEASE DO NOT DELETE!'
PLATFORM_NAME = 'TmoteSky'
NUM_NODES_S = 1
NUM_NODES_P = 93
NUM_NODES_I = 2
IMAGEFILE_S = 'images/demo_image_subscriber_ctp'
IMAGEFILE_P = 'images/demo_image_publishers_ctp'
IMAGEFILE_I = 'images/demo_image_interferers'

NUM_NODES_ALL = NUM_NODES_S + NUM_NODES_P + NUM_NODES_I

logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

try:
    
    access_token = ACCESS_TOKEN
    
    api = COTEFEAPI(server_url = SERVER_URL, access_token=access_token)
    
    me = api.get_current_user()
    
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
    
    print 'access_token: %s' % access_token
    
    api = COTEFEAPI(server_url = SERVER_URL, access_token=access_token)
    
    me = api.get_current_user()
    

logging.info('Your OAuth2 access_token is %s' % access_token)

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

logging.debug('%s virtual nodes retrieved.' % len(my_virtual_nodes))

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

# CREATE A NEW IMAGE 2

my_image_P = api.create_image(
    name = 'Image for Publisher',
    description = DEFAULT_DESCRIPTION,
    imagefile = IMAGEFILE_P,
    experiment = my_experiment)

# CREATE A NEW IMAGE 3

my_image_I = api.create_image(
    name = 'Image for Interferer',
    description = DEFAULT_DESCRIPTION,
    imagefile = IMAGEFILE_I,
    experiment = my_experiment)

exit()

# CREATE A NEW VIRTUAL TASK 0

my_virtual_task_0 = api.create_virtual_task(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_all,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 1

my_virtual_task_1 = api.create_virtual_task(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_1,
    image = my_image_1,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 2

my_virtual_task_2 = api.create_virtual_task(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_2,
    image = my_image_2,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 3

my_virtual_task_3 = api.create_virtual_task(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_3,
    image = my_image_3,
    experiment = my_experiment)
   
# CREATE A NEW VIRTUAL TASK 4

my_virtual_task_4 = api.create_virtual_task(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_3,
    experiment = my_experiment)
