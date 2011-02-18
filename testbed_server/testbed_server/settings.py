import os
import socket

if socket.gethostbyname(socket.gethostname()) == '10.211.55.2':
    print 'DEVELOPMENT'
    DEBUG = True
    DEFAULT_CONTENT_TYPE = 'text/plain'
    DEFAULT_CHARSET = 'utf-8'
else:
    print 'PRODUCTION'
    DEBUG = False
    DEFAULT_CONTENT_TYPE = 'application/json'
    DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
    
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Claudio Donzelli', 'solenoidd@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = os.path.join(PROJECT_PATH, 'sqlite.db')
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = '' 
DATABASE_PORT = ''

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = False


#MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
#MEDIA_URL = '/media/'
#ADMIN_MEDIA_PREFIX = '%sadmin-media/' % MEDIA_URL

SECRET_KEY = 'federatingrocks'

#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#)
#
#TEMPLATE_CONTEXT_PROCESSORS = (
#    'django.core.context_processors.auth',
#    'django.core.context_processors.media',
#    'django.core.context_processors.request',
#)
#
#TEMPLATE_DIRS = ()
#for root, dirs, files in os.walk(PROJECT_PATH):
#    if 'templates' in dirs: TEMPLATE_DIRS += (os.path.join(root, 'templates'),)
#
#if DEBUG:
#    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
#if USE_I18N:
#    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

#if DEBUG:
#    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'urls'



INSTALLED_APPS = (
    
    # Django Applications
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.databrowse',
    
    # Project Applications
    'api',
)

#INTERNAL_IPS = (
#    '127.0.0.1',
#)