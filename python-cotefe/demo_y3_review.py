# in this simple example we create 3 groups of nodes and we install 3 different images on them

from cotefe import client

CONFIG = {
    'DEFAULT_NAME': 'DEMO',
    'DEFAULT_DESCRIPTION': 'COTEFE API DEMO - PLEASE DO NOT DELETE!',
    'PLAFORM_NAME': 'TmoteSky',
    'NUM_NODES_1': 1,
    'NUM_NODES_2': 93,
    'NUM_NODES_3': 2,
    'IMAGE_URL_1': 'http://api2.ge.tt/0/82JYcWC/4/blob/download',
    'IMAGE_URL_2': 'http://api2.ge.tt/0/82JYcWC/2/blob/download',
    'IMAGE_URL_3': 'http://api2.ge.tt/0/82JYcWC/0/blob/download',
}

NUM_NODES_ALL = CONFIG['NUM_NODES_1'] + CONFIG['NUM_NODES_2'] + CONFIG['NUM_NODES_3']

api = client.COTEFEAPI()

# CREATE A NEW PROJECT

my_project = api.create_project(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'])

# CREATE A NEW EXPERIMENT

my_experiment = api.create_experiment(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    project = my_project)

# SEARCH PLATFORM BY NAME

platform_result = api.search_platform(
    by_name = CONFIG['platform'])

my_platform = platform_result[0]

# CREATE A NEW PROPERTY SET

my_property_set = api.create_property_set(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
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
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    virtual_nodes = my_virtual_nodes,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 1

my_virtual_nodegroup_1 = api.create_virtual_nodegroup(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    virtual_nodes = my_virtual_nodes_1,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 2

my_virtual_nodegroup_2 = api.create_virtual_nodegroup(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    virtual_nodes = my_virtual_nodes_2,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL NODEGROUP 3

my_virtual_nodegroup_3 = api.create_virtual_nodegroup(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    virtual_nodes = my_virtual_nodes_3,
    experiment = my_experiment)

# CREATE A NEW IMAGE 1

my_image_1 = api.create_image(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    image_url = CONFIG['IMAGE_URL_1'],
    experiment = my_experiment)

# CREATE A NEW IMAGE 2

my_image_2 = api.create_image(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    image_url = CONFIG['IMAGE_URL_2'],
    experiment = my_experiment)

# CREATE A NEW IMAGE 3

my_image_3 = api.create_image(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    image_url = CONFIG['IMAGE_URL_3'],
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 0

my_virtual_task_0 = api.create_virtual_task(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_all,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 1

my_virtual_task_1 = api.create_virtual_task(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_1,
    image = my_image_1,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 2

my_virtual_task_2 = api.create_virtual_task(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_2,
    image = my_image_2,
    experiment = my_experiment)

# CREATE A NEW VIRTUAL TASK 3

my_virtual_task_3 = api.create_virtual_task(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    action = 'install',
    virtual_nodegroup = my_virtual_nodegroup_3,
    image = my_image_3,
    experiment = my_experiment)
    
# CREATE A NEW VIRTUAL TASK 4

my_virtual_task_4 = api.create_virtual_task(
    name = CONFIG['DEFAULT_NAME'],
    description = CONFIG['DEFAULT_DESCRIPTION'],
    action = 'erase',
    virtual_nodegroup = my_virtual_nodegroup_3,
    experiment = my_experiment)
