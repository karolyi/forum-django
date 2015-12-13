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

from django.utils.translation import ugettext_lazy as _

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ALLOWED_HOSTS = []

SITE_NAME = _('Forum')

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'require',
    'pipeline',
    'debug_toolbar',
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
    # https://docs.djangoproject.com/en/1.8/topics/i18n/translation/#how-django-discovers-language-preference
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

STATICFILES_STORAGE = 'forum.storage.ForumStorage'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.realpath(os.path.join(BASE_DIR, '..', 'static'))

PATH_CDN_ROOT = os.path.join(
    os.path.expanduser('~'), 'Work', 'forum-django-cdn', 'original')

SUPPORTED_LANGUAGES = ('en', 'de', 'hu')

# No extra compressing needed since node-sass does it all
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_COMPILERS = (
    'tools.node_sass_compiler.NodeSassCompiler',
)
PIPELINE_NODE_SASS_BINARY = os.path.join(
    BASE_DIR, 'node_modules', '.bin', 'node-sass')
PIPELINE_CSS = {
    'skins/default/scss/base': {
        'source_filenames': (
            'skins/default/scss/base.scss',
            # 'css/colors/*.css',
            # 'css/layers.css'
        ),
        'output_filename': 'skins/default/css/base-compiled.css',
        # 'extra_context': {
        #     'media': 'screen,projection',
        # },
    },
}

# Django-require config
REQUIRE_BASE_URL = 'skins'
REQUIRE_JS = '../bower_components/requirejs/require.js'
REQUIRE_BUILD_PROFILE = 'app.build.js'
REQUIRE_DEBUG = DEBUG
REQUIRE_STANDALONE_MODULES = {
    'default-skin': {
        'devel_tag': 'separate_tag',
        'relative_baseurl': 'default/js',
        'entry_file_name': 'common.js',
        'out': 'common-built.js',
        'build_profile': 'common.build.js',
    }
}

# ### Forum settings ###
# Default amount of topics to show per category
TOPICS_PER_PAGE = 10
PAGINATOR_ADJACENT_PAGES = 2

# Keep this at the end
try:
    from forum.settings_production import *
except ImportError as e:
    pass
