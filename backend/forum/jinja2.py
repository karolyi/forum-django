from debug_toolbar.panels.templates import TemplatesPanel as BaseTemplatesPanel
from django.conf import settings
from django.utils.html import strip_spaces_between_tags
from django.utils.translation import (
    get_language_from_request, get_language_info)
from jinja2 import nodes
from jinja2.ext import Extension
from rjsmin import jsmin


class SettingsExtension(Extension):
    """
    Puts the settings variable into the global template context.
    """

    def __init__(self, environment):
        super(SettingsExtension, self).__init__(environment)
        environment.globals['django_settings'] = settings


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
        template = self.templates[0]['template']
        if not hasattr(template, 'engine') and hasattr(template, 'backend'):
            template.engine = template.backend
        return super().generate_stats(*args)
