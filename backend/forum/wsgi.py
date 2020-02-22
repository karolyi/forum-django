"""
WSGI config for forum project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')


def get_wsgi_application():
    'Customized returning of a `ForumWSGIHandler`.'
    # @see django.core.wsgi.get_wsgi_application
    from django import setup
    setup(set_prefix=False)
    from .utils.wsgi import ForumWSGIHandler
    return ForumWSGIHandler()


application = get_wsgi_application()
