from django.http.response import \
    HttpResponsePermanentRedirect as redirect_permanent
from django.http.response import HttpResponseRedirect as redirect
from django.utils.translation import ugettext_lazy as _

from forum.exceptions import ForumExceptionBase


class FrontendExceptionBase(ForumExceptionBase):

    """
    Base class for API related exceptions.
    """

    message = _(
        'An exception happened during the frontend response building process.')
    status_code = 400


class FrontendRedirectException(ForumExceptionBase):
    """
    Exceptions resolving in HTTP redirects.
    """

    def __init__(self, url, *args, **kwargs):
        self.url = url
        super(FrontendRedirectException, self).__init__(*args, **kwargs)


class HttpResponseRedirect(FrontendRedirectException):

    """
    Raised when a page is moved (non-permanently, `302 Found`).
    """
    status_code = 302
    message = _('HTTP Redirect (302 Found)')

    def http_response(self):
        return redirect(self.url)


class HttpResponsePermanentRedirect(FrontendRedirectException):

    """
    Raised when a page is moved (non-permanently, `302 Found`).
    """
    status_code = 301
    message = _('HTTP Permanent Redirect (301 Moved Permanently)')
    exception_class = redirect_permanent

    def get_http_response(self) -> redirect_permanent:
        return self.exception_class(self.url)
