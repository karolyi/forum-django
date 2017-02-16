import re

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import ugettext_lazy as _

from ..exceptions import NotProduceable
from .markdown.parser import ForumMarkdownParser

MD_PARSER = ForumMarkdownParser(
    safe_mode='escape', extras=['break-on-newline'])
URL_NONEMBED_REGEX = re.compile(
    pattern=r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
    '(?:%[0-9a-fA-F][0-9a-fA-F]))+', flags=re.MULTILINE)


def collect_cdn(input_md: str) -> str:
    """
    Look for URLs in the Markdown content and download/replace them with
    CDN variants and embeds if they're not those CDN embeds already.
    """


def parse_textarea(request: WSGIRequest):
    """
    Parse input coming from an AJAX request that the richtextarea
    provided.

    Return `md` and `html` as the adjusted Markdown and the generated
    HTML for the preview.

    Raise `NotProduceable` in case of any errors.
    """
    input_md = request.POST.get('text_md')
    input_md = collect_cdn(input_md)
    if input_md is None:
        raise NotProduceable(_(
            'Preview unavailable: text_md parameter not passed'))
    input_html = MD_PARSER.convert(input_md)
    return input_md, input_html
