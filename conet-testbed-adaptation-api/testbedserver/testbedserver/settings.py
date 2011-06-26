
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Claudio Donzelli', 'claudio.donzelli@tu-berlin.de'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_PATH, 'sqlite.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
USE_L10N = False

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'uploads')
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
STATIC_URL = '/static/'

# ADMIN_MEDIA_PREFIX = '%sadmin-media/' % MEDIA_URL

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'uploads'),
    )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(*i9nbgmbw-g582s0(53l+%#_7j)yn#5p(iw3t4z5a=n879xtn'

#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#)

#TEMPLATE_CONTEXT_PROCESSORS = (
#    'django.core.context_processors.auth',
#    'django.core.context_processors.media',
#    'django.core.context_processors.request',
#)

# if DEBUG:
#     TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
# if USE_I18N:
#     TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)
    
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'testbedserver.urls'

#TEMPLATE_DIRS = ()
#for root, dirs, files in os.walk(PROJECT_PATH):
#    if 'templates' in dirs:
#        TEMPLATE_DIRS += (os.path.join(root, 'templates'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
    'django.contrib.databrowse',
    'testbedserver.api',
    # 'registration',
    # 'profiles',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django.request':{
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

# if DEBUG:
#     MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
#     INSTALLED_APPS += ('debug_toolbar',)
    
# DEBUG_TOOLBAR_CONFIG = {
#     "INTERCEPT_REDIRECTS": False,
# }

# DEFAULT_CONTENT_TYPE = 'application/json'
# DEFAULT_CHARSET = 'utf-8'

# ACCOUNT_ACTIVATION_DAYS = 7
# AUTH_PROFILE_MODULE = 'federationserver.api.models.UserResource'

# INTERNAL_IPS = (
#     '127.0.0.1',
# )
