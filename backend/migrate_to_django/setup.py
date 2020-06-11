import logging
import sys
from os import environ

import django

from forum.utils.pathlib import Path

environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')
forum_path = Path(__file__).absolute().parent.parent
sys.path.append(str(forum_path))
# http://django.readthedocs.org/en/latest/releases/1.7.html#standalone-scripts
django.setup()


# Reset django logging setup
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.basicConfig(handlers=[logging.FileHandler(
    Path('~', 'log_migration.log').expanduser(), 'w', 'utf-8')
], level=logging.DEBUG)


def do_setup():
    pass
