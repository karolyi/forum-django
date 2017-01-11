from django.conf import settings
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import ForumAuthForm
from .utils import get_next_url


class LoginView(TemplateView):
    """
    Dealing with login.
    """
    template_name = 'registration/login.html'

    def get(self, request: WSGIRequest):
        """
        Render the login form as empty.
        """
        if request.user.is_authenticated:
            # User already authenticated, go to LOGIN_REDIRECT_URL
            return HttpResponseRedirect(
                redirect_to=settings.LOGIN_REDIRECT_URL)
        return render(
            request=request, template_name=self.template_name, context={
                'next': get_next_url(request=request),
                'auth_form': ForumAuthForm(is_autofocus=True)})

    def post(self, request: WSGIRequest):
        """
        Try to authenticate the user.
        """
        auth_form = ForumAuthForm(
            request=request, data=request.POST, is_autofocus=True)
        if auth_form.is_valid():
            next_url = get_next_url(request)
            login_django(request, auth_form.get_user())
            return HttpResponseRedirect(redirect_to=next_url)
        # Invalid login
        return render(
            request=request, template_name=self.template_name, context={
                'next': get_next_url(request=request),
                'auth_form': auth_form})


def logout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Log the user out, send him back to the url he came from.
    """
    logout_django(request=request)
    return HttpResponseRedirect(redirect_to=get_next_url(request=request))
