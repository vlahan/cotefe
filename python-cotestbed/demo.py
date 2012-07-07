# in this simple example we create a job consisting
# in installing 3 different images on 3 different groups of nodes

import logging
import webbrowser
import config
from cotestbed.client import COTESTBEDAPI
from datetime import date, datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='[%Y-%m-%d %H:%M:%S %z]')

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
    
api = COTESTBEDAPI(server_url=config.SERVER_URL)

# INTRODUCTION
# GETTING THE TESTBED (ROOT RESOURCE)

my_testbed = api.get_testbed()

# INITIALIZE DATABASE

#api.get_nodes()
#api.get_jobs()

# RESOURCE DISCOVERY
# GETTING A LIST OF N NODES MATCHING THE GIVEN PLATFORM

nodes = api.get_nodes(n = config.NUM_NODES_ALL, platform = config.PLATFORM_NAME)

assert len(nodes) == config.NUM_NODES_ALL

# AVAILABILITY DISCOVERY
# GETTING A LIST OF CURRENT JOBS ACCORDING TO THE SPECIFIED TIME SPAN

#date_from = date.today()
#date_to = date_from + timedelta(days = config.CALENDAR_SPAN_DAYS)
#
#jobs = api.get_jobs(date_from = date_from, date_to = date_to)

# JOB RESERVATION
# SCHEDULING A JOB WITH THE GIVEN NODES

my_job = api.create_job( 
    name = config.DEFAULT_NAME,
    description = config.DEFAULT_DESCRIPTION,
    datetime_from = datetime.utcnow() + timedelta(minutes = config.START_JOB_IN_MINUTES),
    datetime_to = datetime.utcnow() + timedelta(minutes = config.END_JOB_IN_MINUTES),
    nodes = nodes)

logging.info('Check your job at %s' % my_job)

# SPLITTING NODES IN 3 GROUPS

my_nodes_S = nodes[0:config.NUM_NODES_S]
my_nodes_P = nodes[config.NUM_NODES_S:config.NUM_NODES_P+1]
my_nodes_I = nodes[config.NUM_NODES_P+1:]

# CHECK NUMBER OF NODES FOR EACH NODE GROUP

logging.debug('%s nodes in group S.' % len(my_nodes_S))
assert len(my_nodes_S) == config.NUM_NODES_S

logging.debug('%s nodes in group P.' % len(my_nodes_P))
assert len(my_nodes_P) == config.NUM_NODES_P

logging.debug('%s nodes in group I.' % len(my_nodes_I))
assert len(my_nodes_I) == config.NUM_NODES_I

# CREATE A NEW WITH ALL NODES

my_nodegroup_ALL = api.create_nodegroup(
    name = 'All Nodes',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    nodes = nodes)
   
assert len(my_nodegroup_ALL.nodes) == config.NUM_NODES_ALL

logging.info('Check your nodegroup ALL at %s' % my_nodegroup_ALL)

# CREATE A NEW NODEGROUP S

my_nodegroup_S = api.create_nodegroup(
    name = 'Subscriber',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    nodes = my_nodes_S)
   
assert len(my_nodegroup_S.nodes) == config.NUM_NODES_S

logging.info('Check your nodegroup S at %s' % my_nodegroup_S)

# CREATE A NEW NODEGROUP 2

my_nodegroup_P = api.create_nodegroup(
    name = 'Publishers',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    nodes = my_nodes_P)
   
assert len(my_nodegroup_S.nodes) == config.NUM_NODES_S

logging.info('Check your nodegroup P at %s' % my_nodegroup_P)

# CREATE A NEW NODEGROUP 3

my_nodegroup_I = api.create_nodegroup(
    name = 'Interferers',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    nodes = my_nodes_I)
   
assert len(my_nodegroup_S.nodes) == config.NUM_NODES_S

logging.info('Check your nodegroup I at %s' % my_nodegroup_I)

# CREATE A NEW IMAGE 1

my_image_S = api.create_image(
    name = 'Image for Subscriber',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    imagefile = config.IMAGEFILE_S)
    
logging.info('Check your image S at %s' % my_image_S)

# CREATE A NEW IMAGE 2

my_image_P = api.create_image(
    name = 'Image for Publisher',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    imagefile = config.IMAGEFILE_P)
    
logging.info('Check your image P at %s' % my_image_P)

# CREATE A NEW IMAGE 3

my_image_I = api.create_image(
    name = 'Image for Interferer',
    description = config.DEFAULT_DESCRIPTION,
    job = my_job,
    imagefile = config.IMAGEFILE_I)
    
logging.info('Check your image I at %s' % my_image_I)

## CREATE A NEW TASK 0
#
#my_task_0 = api.create_task(
#    name = 'Erase all nodes',
#    description = config.DEFAULT_DESCRIPTION,
#    job = my_job,
#    action = 'erase',
#    nodegroup = my_nodegroup_ALL)
#    
#logging.info('Check your task 0 at %s' % my_task_0)
#
## CREATE A NEW TASK 1
#
#my_task_1 = api.create_task(
#    name = 'Install image on Subscriber node',
#    description = config.DEFAULT_DESCRIPTION,
#    job = my_job,
#    action = 'install',
#    nodegroup = my_nodegroup_S,
#    image = my_image_S)
#    
#logging.info('Check your task 1 at %s' % my_task_1)
#
## CREATE A NEW TASK 2
#
#my_task_2 = api.create_task(
#    name = 'Install image on Publisher nodes',
#    description = config.DEFAULT_DESCRIPTION,
#    job = my_job,
#    action = 'install',
#    nodegroup = my_nodegroup_P,
#    image = my_image_P)
#
#logging.info('Check your task 2 at %s' % my_task_2)
#
## CREATE A NEW TASK 3
#
#my_task_3 = api.create_task(
#    name = 'Install image on Interferer nodes',
#    description = config.DEFAULT_DESCRIPTION,
#    job = my_job,
#    action = 'install',
#    nodegroup = my_nodegroup_I,
#    image = my_image_I)
#    
#logging.info('Check your task 3 at %s' % my_task_3)
#   
## CREATE A NEW TASK 4
#
#my_task_4 = api.create_task(
#    name = 'Erase Interferer nodes',
#    description = config.DEFAULT_DESCRIPTION,
#    job = my_job,
#    action = 'erase',
#    nodegroup = my_nodegroup_I)
#
#logging.info('Check your task 4 at %s' % my_task_4)

logging.info('Now check your job again at %s' % my_job)
webbrowser.open(my_job.uri)

# RUNNING THE TASKS

logging.info('# # # # # JOB EXECUTION STARTED # # # # #')

raw_input('(press ENTER when you are ready to execute the next operation)')

logging.info('Erasing all nodes.. ')
my_status_0 = api.erase_image_to_nodegroup(my_nodegroup_ALL)
logging.info('Check the status of the current task at %s' % my_status_0)
webbrowser.open(my_status_0.uri)

raw_input('(press ENTER when you are ready to execute the next operation)')

logging.info('Installing image to Subscriber nodes.. ')
my_status_1 = api.install_image_to_nodegroup(my_nodegroup_S, my_image_S)
logging.info('Check the status of the current task at %s' % my_status_1)
webbrowser.open(my_status_1.uri)

raw_input('(press ENTER when you are ready to execute the next operation)')

logging.info('Installing image to all Publisher nodes.. ')
my_status_2 = api.install_image_to_nodegroup(my_nodegroup_P, my_image_P)
logging.info('Check the status of the current task at %s' % my_status_2)
webbrowser.open(my_status_2.uri)

raw_input('(press ENTER when you are ready to execute the next operation)')

logging.info('Installing image to Interferer nodes.. ')
my_status_3 = api.install_image_to_nodegroup(my_nodegroup_I, my_image_I)
logging.info('Check the status of the current task at %s' % my_status_3)
webbrowser.open(my_status_3.uri)

raw_input('(press ENTER when you are ready to execute the next operation)')

logging.info('Erasing image on Interferer nodes.. ')
my_status_4 = api.erase_image_to_nodegroup(my_nodegroup_I)
logging.info('Check the status of the current task at %s' % my_status_4)
webbrowser.open(my_status_4.uri)

logging.info('# # # # # JOB EXECUTION ENDED # # # # #')