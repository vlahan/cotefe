from djangoappengine.settings_base import *

import os

# Use this if you have a base URL for public downloads
#PUBLIC_DOWNLOAD_URL_BACKEND = 'filetransfers.backends.base_url.public_download_url'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Claudio Donzelli', 'claudio.donzelli@tu-berlin.de'),
)

MANAGERS = ADMINS

INSTALLED_APPS = (
    'djangotoolbox',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    # 'django.contrib.databrowse',
    'api',
    'filetransfers',
    
    'djangoappengine',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

ADMIN_MEDIA_PREFIX = '/media/admin/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = False

ROOT_URLCONF = 'urls'

# Activate django-dbindexer if available
#try:
#    import dbindexer
#    DATABASES['native'] = DATABASES['default']
#    DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native', 'DOMAIN': 'cotefe.net'}
#    INSTALLED_APPS += ('dbindexer',)
#except ImportError:
#    pass
    

APPEND_SLASH = True

############################ NON DJANGO SETTINGS

MEDIA_TYPE = 'application/json'

JSON_INDENT = 4
JSON_ENSURE_ASCII = True

UUID_LENGTH = 8

# TESTBED FEDERATION API
from djangoappengine.utils import on_production_server, have_appserver
if on_production_server:
    SERVER_URL = 'http://api.cotefe.net'
else:
    SERVER_URL = 'http://localhost:8080'

