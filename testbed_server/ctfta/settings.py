import os
# import socket

# next line should automatically allow enabling/disabling of DEBUG
# if socket.gethostbyname(socket.gethostname()) == '10.211.55.2':
DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_CONTENT_TYPE = 'application/json'
DEFAULT_CHARSET = 'utf-8'

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

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


MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '%sadmin-media/' % MEDIA_URL

SECRET_KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcd'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = ()
for root, dirs, files in os.walk(PROJECT_PATH):
    if 'templates' in dirs:
        TEMPLATE_DIRS += (
            os.path.join(root, 'templates'),
        )

if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
if USE_I18N:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)

TEMPLATE_DEBUG = DEBUG

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

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
    'ctfta.api',
    
    # User Management Applications
    'registration', # django-registration
    'profiles', # django-profiles
)

if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar',)

ROOT_URLCONF = 'ctfta.urls'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

AUTH_PROFILE_MODULE = 'api.UserProfile'

INTERNAL_IPS = (
    '127.0.0.1',
)
