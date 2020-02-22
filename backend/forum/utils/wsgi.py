from __future__ import annotations

from random import random

from django.core.handlers.wsgi import WSGIHandler, WSGIRequest
from django.utils.functional import cached_property


class ObjectCache(object):
    'Data class for cache containment, loaded lazily.'

    def __init__(self, request: ForumWSGIRequest = None):
        self._request = random() if request is None else request

    @cached_property
    def user(self):
        from forum.base.utils.cache import UserCache
        return UserCache(request=self._request)

    @cached_property
    def topic(self):
        from forum.base.utils.cache import TopicCache
        return TopicCache(request=self._request)

    @cached_property
    def comment(self):
        from forum.base.utils.cache import CommentCache
        return CommentCache(request=self._request)


class ForumWSGIRequest(WSGIRequest):
    'Customized `WSGIRequest` for the project.'

    @cached_property
    def obj_cache(self) -> ObjectCache:
        return ObjectCache(request=self)


class ForumWSGIHandler(WSGIHandler):
    'Customized `WSGIHandler` for the project.'
    request_class = ForumWSGIRequest
