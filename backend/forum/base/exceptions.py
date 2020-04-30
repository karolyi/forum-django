from django.http.response import \
    HttpResponsePermanentRedirect as redirect_permanent
from django.http.response import HttpResponseRedirect as redirect
from django.http.response import HttpResponseRedirectBase
from django.utils.translation import ugettext_lazy as _

from forum.exceptions import ForumExceptionBase


class FrontendExceptionBase(ForumExceptionBase):

    """
    Base class for API related exceptions.
    """

    message = _(
        'An exception happened during the frontend response building process.')
    status_code = 400


class FrontendRedirectExceptionBase(ForumExceptionBase):
    """
    Exceptions resolving in HTTP redirects.
    """

    def __init__(self, url: str, *args, **kwargs):
        self.url = url
        super(FrontendRedirectExceptionBase, self).__init__(*args, **kwargs)

    def get_httpresponse(self) -> HttpResponseRedirectBase:
        'Return a `HttpResponseRedirectBase`-like object as a response.'
        return self.exception_class(self.url)


class HttpResponseRedirectException(FrontendRedirectExceptionBase):
    'Raised when a page is moved (non-permanently, `301 Found`).'

    status_code = redirect.status_code
    message = _('HTTP Redirect (302 Found)')
    exception_class = redirect


class HttpResponsePermanentRedirectException(FrontendRedirectExceptionBase):
    'Raised when a page is moved (npermanently, `302 Found`).'

    status_code = redirect_permanent.status_code
    message = _('HTTP Permanent Redirect (301 Moved Permanently)')
    exception_class = redirect_permanent
