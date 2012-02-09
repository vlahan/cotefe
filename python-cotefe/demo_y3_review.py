# in this simple example we create 3 groups of nodes and we install 3 different images on them
import webbrowser
import logging
from cotefe.client import COTEFEAPI

# OAUTH2 CONFIGURATIONS

CLIENT_ID = 'd1f30fcc322843fa9cb36d60342fbe3b'
CLIENT_SECRET = '0845a200325a4eee99d4739babd4cb4b'
REDIRECT_URI = 'http://localhost:8090'

access_token = '099a3319f71a489c96e737c4c61532ff'

# EXPERIMENT CONFIGURATION

DEFAULT_NAME = 'DEMO'
DEFAULT_DESCRIPTION = 'COTEFE API DEMO - PLEASE DO NOT DELETE!'
PLAFORM_NAME = 'TmoteSky'
NUM_NODES_S = 1
NUM_NODES_P = 93
NUM_NODES_I = 2
IMAGE_URL_S = 'http://'
IMAGE_URL_P = 'http://'
IMAGE_URL_I = 'http://'

NUM_NODES_ALL = NUM_NODES_S + NUM_NODES_P + NUM_NODES_I

logging.basicConfig(
        level=logging.INFO,
        # filename='%s.log' % __file__, filemode='w',
        format='%(asctime)s %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S %z]',
    )

if not access_token:
    
    unauthorized_api = COTEFEAPI(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = REDIRECT_URI)
    
    authorize_url = unauthorized_api.get_authorize_url()
    
    webbrowser.open(authorize_url)
    
    print "Visit this page and authorize access in your browser: ", authorize_url
    
    code = raw_input("Paste in code in query string after redirect: ").strip()
    
    access_token = unauthorized_api.exchange_code_for_access_token(code)
    
    print "access_token: ", access_token

api = COTEFEAPI(access_token=access_token)

me = api.get_current_user()

logging.info('me = %s' % me)

# CREATE A NEW PROJECT

my_project = api.create_project(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION)

logging.info('My Project = %s' % my_project)

# CREATE A NEW EXPERIMENT

my_experiment = api.create_experiment(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    project = my_project)

logging.info('My Experiment = %s' % my_experiment)

# SEARCH PLATFORM BY NAME

platform_result = api.search_platform(
    name = PLAFORM_NAME)

my_platform = platform_result[0]

logging.info('My Platform = %s' % my_experiment)

exit()

# CREATE A NEW PROPERTY SET

my_property_set = api.create_property_set(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    platform = my_platform,
    num_nodes = NUM_NODES_ALL,
    experiment = my_experiment)

# GET VIRTUAL NODES

my_virtual_nodes = api.get_virtual_nodes(
    experiment = my_experiment)

# CHECK NUMBER OF NODES

assert len(my_virtual_nodes) == NUM_NODES_ALL

# SPLIT VIRTUAL NODES IN 3 GROUPS

my_virtual_nodes_1 = my_virtual_nodes[0:CONFIG['NUM_NODES_1']]
my_virtual_nodes_2 = my_virtual_nodes[CONFIG['NUM_NODES_1']:CONFIG['NUM_NODES_2']+1]
my_virtual_nodes_3 = my_virtual_nodes[CONFIG['NUM_NODES_2']+1:]

# CHECK NUMBER OF NODES FOR EACH NODE GROUP

assert len(my_virtual_nodes_1) == CONFIG['NUM_NODES_1']
assert len(my_virtual_nodes_2) == CONFIG['NUM_NODES_2']
assert len(my_virtual_nodes_3) == CONFIG['NUM_NODES_3']

# CREATE A NEW VIRTUAL NODEGROUP WITH ALL NODES

my_virtual_nodegroup_all = api.create_virtual_nodegroup(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 1

my_virtual_nodegroup_1 = api.create_virtual_nodegroup(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_1,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 2

my_virtual_nodegroup_2 = api.create_virtual_nodegroup(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_2,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 3

my_virtual_nodegroup_3 = api.create_virtual_nodegroup(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_3,
    experiment = my_experiment)

# CREATE A NEW IMAGE 1

my_image_1 = api.create_image(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    image_url = CONFIG['IMAGE_URL_1'],
    experiment = my_experiment)

# CREATE A NEW IMAGE 2

my_image_2 = api.create_image(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    image_url = CONFIG['IMAGE_URL_2'],
    experiment = my_experiment)

# CREATE A NEW IMAGE 3

my_image_3 = api.create_image(
    name = DEFAULT_NAME,
    description = DEFAULT_DESCRIPTION,
    image_url = CONFIG['IMAGE_URL_3'],
    experiment = my_experiment)

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
