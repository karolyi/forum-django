"""
Django settings for forum project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import mimetypes

# Keep this at the beginning, after module imports
try:
    from forum.settings_production import *
except ImportError as e:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'FORUM_SECRET_KEY', '(tfz61pc=z34-(m)t#ul3^pf%405xb+$=mwy&ozd-h$kq+^b&p')

# SECURITY WARNING: don't run with debug turned on in production!
try:
    DEBUG
except NameError:
    DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'forum',
    'base',
    'cdn',
    'event',
    'messaging',
    'crowdfunding',
    'poll',
    'rating',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'forum.urls'

WSGI_APPLICATION = 'forum.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'forum-django',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'OPTIONS': {
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

if DEBUG:
    # For static serving in development
    mimetypes.add_type('text/x-scss', '.scss', True)
    mimetypes.add_type('image/x-sass', '.sass', True)
    mimetypes.add_type('image/svg+xml', '.svg', True)
    mimetypes.add_type('image/svg+xml', '.svgz', True)

TMP_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'tmp'))
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

LOG_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'logs'))
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# Logging setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': (
                '[%(asctime)s] %(levelname)s '
                '[%(name)s:%(lineno)s] %(message)s'),
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django-log.txt'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

PATH_CDN_ROOT = os.path.join(
    os.path.expanduser('~'), 'Work', 'forum-django-cdn', 'original')

SUPPORTED_LANGUAGES = ('en', 'de', 'hu')

# Keep this at the end
try:
    from forum.settings_production import *
except ImportError as e:
    pass
