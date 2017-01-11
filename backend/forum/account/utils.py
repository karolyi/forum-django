from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import validate_host


def strip_hostname(referrer: str) -> str:
    """
    Strip the hostname from the HTTP referrer, while checking if it's
    one of our allowed hostnames.

    Raise `ValueError` if the referrer was invalid, return the
    path & query part when it's one of the allowed hostnames.
    """
    parsed_url = urlparse(url=referrer)
    hostname = parsed_url.hostname
    if parsed_url.hostname is None:
        hostname = ''
    is_allowed = validate_host(
        host=hostname, allowed_hosts=settings.ALLOWED_HOSTS)
    if not is_allowed:
        raise ValueError()
    return urlunparse(
        components=('', '', parsed_url.path, '', parsed_url.query, ''))


def get_next_url(request: WSGIRequest) -> str:
    """
    Calculate the URL to redirect to after a successful login.
    It's either:

    - the `next` parameter from the HTTP POST
    - the HTTP referrer
    - `settings.LOGIN_REDIRECT_URL`.

    Return the URL to redirect to.
    """
    post_next = request.POST.get('next')
    if post_next is not None:
        return post_next
    referrer = request.META.get('HTTP_REFERER')
    if referrer is None:
        # No referrer
        return settings.LOGIN_REDIRECT_URL
    try:
        return strip_hostname(referrer=referrer)
    except ValueError:
        # Invalid referrer, might be useful to log here later
        return settings.LOGIN_REDIRECT_URL
