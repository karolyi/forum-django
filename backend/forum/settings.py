"""
Django settings for forum project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import mimetypes
from os import environ
from pathlib import Path

from django.utils.translation import ugettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS

# Keep this at the beginning, after module imports
try:
    from forum.settings_override import *  # NOQA
except ImportError:
    pass

BASE_DIR = Path(__file__).absolute().parent.parent
DIR_BACKEND = BASE_DIR
DIR_FRONTEND = BASE_DIR.parent.joinpath('frontend')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = locals().get('SECRET_KEY') or environ.get(
    'FORUM_SECRET_KEY', '(tfz61pc=z34-(m)t#ul3^pf%405xb+$=mwy&ozd-h$kq+^b&p')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = locals().get('DEBUG', True)

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

ALLOWED_HOSTS = \
    locals().get('ALLOWED_HOSTS') or ['test.localdomain', 'localhost']

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

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#how-django-discovers-language-preference
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    DIR_BACKEND.joinpath('static'),
    # We do this so that django's collectstatic copies or our bundles to
    # the STATIC_ROOT or syncs them to whatever storage we use.
    DIR_FRONTEND.joinpath('dist'),
)

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'assets/',
        'STATS_FILE': DIR_FRONTEND.joinpath('webpack', 'stats.json'),
        'CACHE': not DEBUG
    }
}

ROOT_URLCONF = 'forum.urls'

WSGI_APPLICATION = 'forum.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = locals().get('DATABASES') or dict(default=dict(
    ENGINE='django.db.backends.mysql', NAME='forum-django', USER='root',
    PASSWORD='', HOST='127.0.0.1', PORT=3306, OPTIONS=dict(
        sql_mode='STRICT_ALL_TABLES', charset='utf8mb4')))

AUTH_USER_MODEL = 'forum_base.User'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.AllowAllUsersModelBackend',)

TEST_RUNNER = 'forum.utils.DjangoTestRunner'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

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
    INSTALLED_APPS += (
        'debug_toolbar',
        # 'debug_panel',
    )
    INTERNAL_IPS = ['127.0.0.1']
    MIDDLEWARE = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # 'debug_panel.middleware.DebugPanelMiddleware',
    ) + MIDDLEWARE
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

SHELL_PLUS_PYGMENTS_FORMATTER_KWARGS = dict(bg='dark')
# Truncate sql queries to this number of characters
SHELL_PLUS_PRINT_SQL_TRUNCATE = 10000

TMP_DIR = DIR_BACKEND.joinpath('tmp')
TMP_DIR.mkdir(exist_ok=True)

LOG_DIR = DIR_BACKEND.joinpath('logs')
LOG_DIR.mkdir(exist_ok=True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.parent.joinpath('static')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent.joinpath('media')

_path_orig = Path('~', 'Work', 'forum-django-cdn', 'original').expanduser()
CDN = locals().get('CDN') or dict(
    PATH_ORIG=_path_orig,
    URL_PREFIX='https://example.cdnhost.com',  # Avoid the trailing slash
    # See https://getbootstrap.com/docs/4.4/layout/grid/#grid-options
    # The order is important, <picture> tag generates along this
    IMAGESIZE=dict(xs=576, sm=768, md=992, xl=1200),
    PATH_SIZES=dict(
        original=_path_orig, xs=_path_orig.parent.joinpath('xs'),
        sm=_path_orig.parent.joinpath('sm'),
        md=_path_orig.parent.joinpath('md'),
        lg=_path_orig.parent.joinpath('lg'))
    )

CDN['URLPREFIX_SIZE'] = dict()
for size, path in CDN['PATH_SIZES'].items():  # type: str, Path
    path.mkdir(parents=True, exist_ok=True)
    CDN['URLPREFIX_SIZE'][size] = '/'.join((CDN['URL_PREFIX'], size))

LANGUAGES = locals().get('LANGUAGES') or (
    ('en', _('English')),
    ('de', _('German')),
    ('hu', _('Hungarian')))

# ### Forum settings ###
PAGINATOR_MAX_COMMENTS_PER_PAGE = 50
PAGINATOR_TOPICS_PER_PAGE = 10
PAGINATOR_DEFAULT_ADJACENT_PAGES = 2

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'forum:account:login'

CRXFORUM_CONNECTION = locals().get('CRXFORUM_CONNECTION') or dict(
    db='crxforum', user='crxforum', passwd='test123', charset='utf8',
    host='localhost')

# Keep this at the very bottom of settings.py
try:
    from forum.settings_override import *  # NOQA
except ImportError:
    pass
