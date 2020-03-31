from functools import lru_cache
from typing import Dict, List, Optional

from debug_toolbar.panels.templates import TemplatesPanel as BaseTemplatesPanel
from django.conf import settings
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.handlers.wsgi import WSGIRequest
from django.utils.html import strip_spaces_between_tags
from django.utils.translation import (
    get_language_from_request, get_language_info)
from jinja2 import nodes
from jinja2.ext import Extension
from rjsmin import jsmin

ForumAuthForm = None


class JsMinExtension(Extension):
    """
    Removes whitespace between JavaScript tags, including tab and
    newline characters.
    """

    tags = {'jsmin'}

    def parse(self, parser):
        lineno = parser.stream.__next__().lineno
        body = parser.parse_statements(['name:endjsmin'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_whitespace_js', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_whitespace_js(self, caller=None):
        if settings.DEBUG:
            # Debug mode, no minification
            return caller().strip()
        return jsmin(caller().strip())

# https://github.com/coffin/coffin/blob/master/coffin/common.py


class SpacelessExtension(Extension):
    """
    Removes whitespace between HTML tags, including tab and
    newline characters.

    Works exactly like Django's own tag.
    """

    tags = set(['spaceless'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(['name:endspaceless'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_spaces', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        return strip_spaces_between_tags(caller().strip())


class CommentExtension(Extension):
    """
    Skips the content within the comment/endcomment tag.
    """

    tags = set(['comment'])

    def parse(self, parser):
        next(parser.stream)
        parser.parse_statements(['name:endcomment'], drop_needle=True)
        return []


class MyLanguageInfoExtension(Extension):
    """
    An assigment tag for Jinja, setting a language info dictionary.

    Samples hacked together from:
    http://stackoverflow.com/a/23170408/1067833
    https://github.com/coffin/coffin/blob/master/coffin/static.py
    """

    tags = set(['get_my_language_info'])

    def parse(self, parser):
        stream = parser.stream
        lineno = next(stream).lineno

        ctx_ref = nodes.ContextReference()
        call_node = self.call_method(
            '_get_current_language_info', [ctx_ref], lineno=lineno)

        if stream.next_if('name:as'):
            var = nodes.Name(stream.expect('name').value, 'store')
            return nodes.Assign(var, call_node).set_lineno(lineno)
        else:
            return nodes.Output([call_node]).set_lineno(lineno)

    def _get_current_language_info(self, context):
        lang_code = get_language_from_request(request=context['request'])
        return get_language_info(lang_code=lang_code)


class TemplatesPanel(BaseTemplatesPanel):
    """
    A fix for django debug toolbar.

    http://stackoverflow.com/a/39036820/1067833
    """

    def generate_stats(self, *args):
        if not self.templates:
            return
        template = self.templates[0]['template']
        if not hasattr(template, 'engine') and hasattr(template, 'backend'):
            template.engine = template.backend
        return super().generate_stats(*args)


@lru_cache(maxsize=20)
def paginator_generic_get_list(
    current_no: int, num_pages: int,
    adjacent_pages: int = settings.PAGINATOR_DEFAULT_ADJACENT_PAGES
) -> Optional[List[Dict]]:
    'Generate a paginator list with ellipsis.'
    result = []
    start_idx = max(current_no - adjacent_pages, 1)
    if start_idx <= 3:
        start_idx = 1
    else:
        result.extend([dict(number=1, type='number'), dict(type='ellipsis')])
    end_idx = current_no + adjacent_pages + 1
    do_end_ellipsis = True
    if end_idx >= num_pages - 1:
        end_idx = num_pages + 1
        do_end_ellipsis = False
    result.extend([
        dict(number=x, type='number') for x in range(start_idx, end_idx)])
    if do_end_ellipsis:
        result.extend([
            dict(type='ellipsis'), dict(number=num_pages, type='number')])
    return result


def forum_auth_form():
    global ForumAuthForm
    if ForumAuthForm is None:
        from forum.account.forms import ForumAuthForm
    return ForumAuthForm


@lru_cache(maxsize=100)
def is_topic_comment_visible(
        comment, show_invisible: bool, request: WSGIRequest,
        cache_key: str = 'topic-comment-listing') -> bool:
    """
    Tell the templating engine if a given comment should or shouldn't be
    visible in a given user context.

    Return `True` if yes, `False` when no.
    """
    if show_invisible:
        return True
    if not comment.topic.is_enabled:
        return False
    is_admin = request.user.is_staff or request.user.is_superuser
    if comment.topic.is_staff_only and not is_admin:
        # Staff only topic, but the user is non-staff:
        return False
    return True


class ForumToolsExtension(Extension):
    """
    Puts the settings variable and other utilities into the global
    template context.
    """

    def __init__(self, environment):
        super(ForumToolsExtension, self).__init__(environment)
        environment.globals['django_settings'] = settings
        environment.globals['forum_auth_form'] = forum_auth_form()
        environment.globals['is_topic_comment_visible'] = \
            is_topic_comment_visible
        environment.globals['paginator_generic_get_list'] = \
            paginator_generic_get_list
        environment.filters['naturaltime'] = naturaltime
        environment.globals['messages'] = messages
