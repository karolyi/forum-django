"""
Django settings for forum project.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import mimetypes
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.utils.translation import ugettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS

# Keep this at the beginning, after module imports
try:
    from forum.settings_production import *  # NOQA
except ImportError as e:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DIR_BACKEND = BASE_DIR
DIR_FRONTEND = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'FORUM_SECRET_KEY', '(tfz61pc=z34-(m)t#ul3^pf%405xb+$=mwy&ozd-h$kq+^b&p')

# SECURITY WARNING: don't run with debug turned on in production!
try:
    DEBUG  # NOQA
except NameError:
    DEBUG = True

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'app_dirname': 'jinja2',
            'match_extension': None,
            # 'match_regex': r'^(?!debug_toolbar/).*',
            'newstyle_gettext': True,
            # https://github.com/niwinz/django-jinja/issues/140#issuecomment-145696119
            'filters': {
                'add_class':
                    'widget_tweaks.templatetags.widget_tweaks.add_class',
                'set_attr':
                    'widget_tweaks.templatetags.widget_tweaks.set_attr',
            },
            'extensions': DEFAULT_EXTENSIONS + [
                'django_jinja.builtins.extensions.CsrfExtension',
                'django_jinja.builtins.extensions.DjangoExtraFiltersExtension',
                'webpack_loader.contrib.jinja2ext.WebpackExtension',
                'jinja2.ext.with_',
                'jinja2.ext.i18n',
                'jinja2.ext.do',
                'forum.jinja2.SpacelessExtension',
                'forum.jinja2.ForumToolsExtension',
                'forum.jinja2.JsMinExtension',
                'forum.jinja2.CommentExtension',
                'forum.jinja2.MyLanguageInfoExtension',
            ],
            'bytecode_cache': {
                'name': 'default',
                'backend': 'django_jinja.cache.BytecodeCache',
                'enabled': not DEBUG,
            },
            'autoescape': False,
            'auto_reload': DEBUG,
            'translation_engine': 'django.utils.translation',
        },
    },
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
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            # 'loaders': [
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]

ALLOWED_HOSTS = ['test.localdomain']

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
    'webpack_loader',
    'django_jinja',
    'forum',
    'forum.account',
    'forum.base',
    'forum.cdn',
    'forum.crowdfunding',
    'forum.event',
    'forum.messaging',
    'forum.poll',
    'forum.rating',
    'forum.rest_api',
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
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    # We do this so that django's collectstatic copies or our bundles to
    # the STATIC_ROOT or syncs them to whatever storage we use.
    os.path.join(DIR_FRONTEND, 'dist'),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'assets/',
        'STATS_FILE': os.path.join(DIR_FRONTEND, 'webpack', 'stats.json'),
        'CACHE': not DEBUG
    }
}

ROOT_URLCONF = 'forum.urls'

WSGI_APPLICATION = 'forum.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'forum-django',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'OPTIONS': {
            'sql_mode': 'STRICT_ALL_TABLES',
            'charset': 'utf8mb4'
        }
    }
}

AUTH_USER_MODEL = 'forum_base.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.AllowAllUsersModelBackend',)

TEST_RUNNER = 'forum.utils.DjangoTestRunner'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

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
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',)
    INTERNAL_IPS = ('127.0.0.1',)
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        # original broken by django-jinja, remove this whole block later
        'forum.jinja2.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

TMP_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'tmp'))
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

LOG_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'logs'))
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.realpath(os.path.join(BASE_DIR, '..', 'static'))

PATH_CDN_ROOT = os.path.join(
    os.path.expanduser('~'), 'Work', 'forum-django-cdn', 'original')
CDN_URL_PREFIX = 'https://example.cdnhost.com/'

LANGUAGES = (
    ('en', _('English')),
    ('de', _('German')),
    ('hu', _('Hungarian')))

# ### Forum settings ###
# Default amount of topics to show per category
PAGINATOR_MAX_COMMENTS_LISTED = 50
PAGINATOR_MAX_PAGES_TOPICLIST = 10

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'forum:account:login'

# Keep this at the very bottom of settings.py
try:
    from forum.settings_production import *  # NOQA
except ImportError as e:
    pass
