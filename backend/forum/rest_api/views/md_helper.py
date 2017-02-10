from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from ..exceptions import NotProduceable
from ..utils.md import parse_textarea


@require_POST
@login_required
def md_parser(request: WSGIRequest) -> JsonResponse:
    """
    Parse an MD formatted textarea content, download images and links,
    and return a formatted HTML content for display.

    Raise `NotProduceable` in case of any errors.
    """
    try:
        md, html = parse_textarea(request)
    except NotProduceable as e:
        return e.json_response()
    return JsonResponse({'html': html, 'md': md})
