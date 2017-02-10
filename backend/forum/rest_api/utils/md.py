from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import ugettext_lazy as _

from ..exceptions import NotProduceable
from .markdown.parser import ForumMarkdownParser

MD_PARSER = ForumMarkdownParser(
    safe_mode='escape', extras=['break-on-newline'])


def parse_textarea(request: WSGIRequest):
    """
    Parse input coming from an AJAX request that the richtextarea
    provided.

    Return `md` and `html` as the adjusted Markdown and the generated
    HTML for the preview.

    Raise `NotProduceable` in case of any errors.
    """
    input_md = request.POST.get('text_md')
    if input_md is None:
        raise NotProduceable(_(
            'Preview unavailable: text_md parameter not passed'))
    return input_md, MD_PARSER.convert(input_md)
