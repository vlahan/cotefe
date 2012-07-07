# in this simple example we create a testbed indepented experiment with cooperating objects
# the experiment consists in installing 3 different images on 3 different groups of nodes

import logging
import webbrowser
import config
from cotefe.client import COTEFEAPI
from datetime import date, datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='[%Y-%m-%d %H:%M:%S %z]')

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

try:
    
    # AUTHORIZATION SUCCEDED  
    api = COTEFEAPI(server_url=config.SERVER_URL, access_token=config.ACCESS_TOKEN)
    
except:
    
    # OAUTH 2.0 HANDSHAKE
    unauthorized_api = COTEFEAPI(server_url=config.SERVER_URL, client_id=config.CLIENT_ID, client_secret=config.CLIENT_SECRET, redirect_uri=config.REDIRECT_URI)
    authorize_url = unauthorized_api.get_authorize_url()
    webbrowser.open(authorize_url)
    print 'Visit this page and authorize access in your browser:', authorize_url
    code = raw_input('Paste in code in query string after redirect: ').strip()
    access_token = unauthorized_api.exchange_code_for_access_token(code)
    
    # AUTHORIZATION SUCCEDED  
    api = COTEFEAPI(server_url=config.SERVER_URL, access_token=access_token)

    logging.info('Your OAuth2 access_token is %s' % access_token)

me = api.get_current_user()

logging.info('Check your account information at %s' % me)

# CREATE A NEW PROJECT

my_project = api.create_project(
    name = config.DEFAULT_NAME,
    description = config.DEFAULT_DESCRIPTION)

logging.info('Check your project at %s' % my_project)

# CREATE A NEW EXPERIMENT

my_experiment = api.create_experiment(
    name = config.DEFAULT_NAME,
    description = config.DEFAULT_DESCRIPTION,
    project = my_project)

logging.info('Check your experiment at %s' % my_experiment)

# SEARCH PLATFORM BY NAME

my_platform = api.get_platform(
    platform_id = config.PLATFORM_NAME)

logging.info('Check the platform "%s" at %s' % (config.PLATFORM_NAME, my_platform))

# CREATE A NEW PROPERTY SET

my_property_set = api.create_property_set(
    name = config.DEFAULT_NAME,
    description = config.DEFAULT_DESCRIPTION,
    platform = my_platform,
    num_nodes = config.NUM_NODES_ALL,
    experiment = my_experiment)

logging.info('Check your property set at %s' % my_property_set)

# GET VIRTUAL NODES

my_virtual_nodes = api.get_virtual_nodes(
   experiment = my_experiment)

# CHECK NUMBER OF NODES

logging.info('%s virtual nodes retrieved.' % len(my_virtual_nodes))

assert len(my_virtual_nodes) == config.NUM_NODES_ALL

## SPLIT VIRTUAL NODES IN 3 GROUPS

my_virtual_nodes_S = my_virtual_nodes[0:config.NUM_NODES_S]
my_virtual_nodes_P = my_virtual_nodes[config.NUM_NODES_S:config.NUM_NODES_P+1]
my_virtual_nodes_I = my_virtual_nodes[config.NUM_NODES_P+1:]

## CHECK NUMBER OF NODES FOR EACH NODE GROUP

logging.debug('%s virtual nodes in group S.' % len(my_virtual_nodes_S))

assert len(my_virtual_nodes_S) == config.NUM_NODES_S

logging.debug('%s virtual nodes in group P.' % len(my_virtual_nodes_P))
assert len(my_virtual_nodes_P) == config.NUM_NODES_P

logging.debug('%s virtual nodes in group I.' % len(my_virtual_nodes_I))
assert len(my_virtual_nodes_I) == config.NUM_NODES_I

# CREATE A NEW VIRTUAL NODEGROUP WITH ALL NODES

my_virtual_nodegroup_ALL = api.create_virtual_nodegroup(
    name = 'All Nodes',
    description = config.DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_ALL.virtual_nodes) == config.NUM_NODES_ALL

logging.info('Check your virtual nodegroup ALL at %s' % my_virtual_nodegroup_ALL)

# CREATE A NEW VIRTUAL NODEGROUP S

my_virtual_nodegroup_S = api.create_virtual_nodegroup(
    name = 'Subscriber',
    description = config.DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_S,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == config.NUM_NODES_S

logging.info('Check your virtual nodegroup S at %s' % my_virtual_nodegroup_S)

# CREATE A NEW VIRTUAL NODEGROUP 2

my_virtual_nodegroup_P = api.create_virtual_nodegroup(
    name = 'Publishers',
    description = config.DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_P,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == config.NUM_NODES_S

logging.info('Check your virtual nodegroup P at %s' % my_virtual_nodegroup_P)

# CREATE A NEW VIRTUAL NODEGROUP 3

my_virtual_nodegroup_I = api.create_virtual_nodegroup(
    name = 'Interferers',
    description = config.DEFAULT_DESCRIPTION,
    virtual_nodes = my_virtual_nodes_I,
    experiment = my_experiment)
   
assert len(my_virtual_nodegroup_S.virtual_nodes) == config.NUM_NODES_S

logging.info('Check your virtual nodegroup I at %s' % my_virtual_nodegroup_I)

# CREATE A NEW IMAGE 1

my_image_S = api.create_image(
    name = 'Image for Subscriber',
    description = config.DEFAULT_DESCRIPTION,
    imagefile = config.IMAGEFILE_S,
    experiment = my_experiment)
    
logging.info('Check your image S at %s' % my_image_S)

# CREATE A NEW IMAGE 2

my_image_P = api.create_image(
    name = 'Image for Publisher',
    description = config.DEFAULT_DESCRIPTION,
    imagefile = config.IMAGEFILE_P,
    experiment = my_experiment)
    
logging.info('Check your image P at %s' % my_image_P)

# CREATE A NEW IMAGE 3

my_image_I = api.create_image(
    name = 'Image for Interferer',
    description = config.DEFAULT_DESCRIPTION,
    imagefile = config.IMAGEFILE_I,
    experiment = my_experiment)
    
logging.info('Check your image I at %s' % my_image_I)

# CREATE A NEW VIRTUAL TASK 0

my_virtual_task_0 = api.create_virtual_task(
    name = 'Erase all nodes',
    description = config.DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_ALL,
    image = None,
    experiment = my_experiment)
    
logging.info('Check your virtual task 0 at %s' % my_virtual_task_0)

# CREATE A NEW VIRTUAL TASK 1

my_virtual_task_1 = api.create_virtual_task(
    name = 'Install image on Subscriber node',
    description = config.DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_S,
    image = my_image_S,
    experiment = my_experiment)
    
logging.info('Check your virtual task 1 at %s' % my_virtual_task_1)

# CREATE A NEW VIRTUAL TASK 2

my_virtual_task_2 = api.create_virtual_task(
    name = 'Install image on Publisher nodes',
    description = config.DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_P,
    image = my_image_P,
    experiment = my_experiment)

logging.info('Check your virtual task 2 at %s' % my_virtual_task_2)

# CREATE A NEW VIRTUAL TASK 3

my_virtual_task_3 = api.create_virtual_task(
    name = 'Install image on Interferer nodes',
    description = config.DEFAULT_DESCRIPTION,
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_I,
    image = my_image_I,
    experiment = my_experiment)
    
logging.info('Check your virtual task 3 at %s' % my_virtual_task_3)
   
# CREATE A NEW VIRTUAL TASK 4

my_virtual_task_4 = api.create_virtual_task(
    name = 'Erase Interferer nodes',
    description = config.DEFAULT_DESCRIPTION,
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_I,
    image = None,
    experiment = my_experiment)

logging.info('Check your virtual task 4 at %s' % my_virtual_task_4)

logging.info('Now check your experiment again at %s' % my_experiment)

webbrowser.open(my_experiment.uri)
