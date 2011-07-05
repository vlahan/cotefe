from djangoappengine.settings_base import *

import os

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
    'django.contrib.databrowse',
    'federationserver.api',

    'djangoappengine',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = False

ROOT_URLCONF = 'urls'

# from djangoappengine.settings_base import *
# DATABASES['default']['HIGH_REPLICATION'] = True
