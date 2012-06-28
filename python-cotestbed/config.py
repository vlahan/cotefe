
# SERVER_URL = 'http://127.0.0.1:8001'
SERVER_URL = 'https://www.twist.tu-berlin.de:8001'

# EXPERIMENT CONFIGURATION

DEFAULT_NAME = 'DEMO'
DEFAULT_DESCRIPTION = 'DEMO - PLEASE DO NOT DELETE!'
PLATFORM_NAME = 'tmotesky'
NUM_NODES_S = 1
NUM_NODES_P = 3 # 93
NUM_NODES_I = 2
IMAGEFILE_S = 'images/demo_image_subscriber_ctp'
IMAGEFILE_P = 'images/demo_image_publishers_ctp'
IMAGEFILE_I = 'images/demo_image_interferers'

NUM_NODES_ALL = NUM_NODES_S + NUM_NODES_P + NUM_NODES_I

CALENDAR_SPAN_DAYS = 7
START_JOB_IN_MINUTES = 1
END_JOB_IN_MINUTES   = 61
