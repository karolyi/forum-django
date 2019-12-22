import os
import sys
import django
import logging

allowed_filters = ('image_downloader', 'commentparser')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')
forum_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(forum_path)
# http://django.readthedocs.org/en/latest/releases/1.7.html#standalone-scripts
django.setup()


# Reset django logging setup
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.basicConfig(handlers=[logging.FileHandler(
    'log_migration.log', 'w', 'utf-8')], level=logging.DEBUG)


def do_setup():
    pass
