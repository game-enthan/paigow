# Django settings for paigow project.

import os
import sys

# The project starts at mainsite/ rather than top-level at the application,
# but we use a lot of things from the paigow/ folder.  Create a global for
# the paigow folder as well.
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))   # mainsite/
(PAIGOW_APP_PATH, DUMMY) = os.path.split(os.path.dirname(__file__))
PAIGOW_PATH = PAIGOW_APP_PATH + "/paigow"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Rudi Sherry', 'rudisherry666@gmail.com'),
)

MANAGERS = ADMINS

# set up the database.  For local development it's easiest to
# use sqlite3, so we do that, and we depend on the developer having
# set up an environment variable on their machine called "LOCAL_DEV"
# which is set to 'true'.
try:
  if (bool(os.environ.get('LOCAL_DEV', False))):
    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': PROJECT_PATH + '/database/paigow.sqlite',
        'USER': '', # not needed since we're local, default is always trusted
        'PASSWORD': '',
        'HOST': '',
      }
    }
  else:
    # In heroku (where we deploy on the web), we use postgres; existence
    # of the postgres database is set up by previous commands to heroku
    # (TBD: make that some sort of automatic script), and the connection
    # to it from python is set up by the file 'requirements.txt' which
    # includes psycopg2 (the python extension for postgres).
    #
    # dj_database_url is an egg that uses DATABASE_URL to find the
    # correct database, and that is also set up by previous heroku
    # commands.
    import dj_database_url
    DATABASES = {
      'default': dj_database_url.config(default='postgres://localhost')
    }
except:
  # uh-oh, something went wrong but we don't know what.
  print "Unexpected error creating DATABASES:", sys.exc_info()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_PATH + "/static/",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's1upu83yei)f#39&amp;1473$atc63=80*q==jv*c%n#f03crfm68r'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
  # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  # Uncomment the next line for simple clickjacking protection:
  # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# this allows the messages app/framework to get messages into pages
TEMPLATE_CONTEXT_PROCESSORS = (
  'django.core.context_processors.request',
  'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'mainsite.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'paigow.wsgi.application'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  PAIGOW_PATH + '/templates/',
  PROJECT_PATH + '/templates/',
)

INSTALLED_APPS = (
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  # Uncomment the next line to enable the admin:
  # 'django.contrib.admin',
  # Uncomment the next line to enable admin documentation:
  # 'django.contrib.admindocs',
  'paigow',
)

# For testing we get fixtures from here
FIXTURE_DIRS = (
  PAIGOW_PATH + '/fixtures/',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

