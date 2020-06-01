from django.utils.cache import add_never_cache_headers

from .wsgi import ForumWSGIRequest


class DisableClientSideCachingMiddleware(object):
    'https://stackoverflow.com/a/5882033/1067833'

    def __init__(self, get_response):
        'One-time configuration and initialization.'
        self.get_response = get_response

    def __call__(self, request: ForumWSGIRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        add_never_cache_headers(response)

        # Code to be executed for each request/response after
        # the view is called.

        return response
