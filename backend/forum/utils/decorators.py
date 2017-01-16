from functools import wraps

from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404


def logged_in_or_404(view_func):
    """
    Decorator for views that raises `Http404` when the user is not
    logged in.
    """
    def _checklogin(request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            # The user is not logged in, raise Http404
            raise Http404
        return view_func(request, *args, **kwargs)

    return wraps(view_func)(_checklogin)
