from typing import Union

from django.conf import settings
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from forum.base.models import IntroductionModification

from .forms import ForumAuthForm, IntroductionModificationForm, SettingsForm
from .utils import get_next_url


class LoginView(View):
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


@login_required
def logout(request: WSGIRequest) -> HttpResponseRedirect:
    """
    Log the user out, send him back to the url he came from.
    """
    logout_django(request=request)
    return HttpResponseRedirect(redirect_to=get_next_url(request=request))


@method_decorator(decorator=login_required, name='dispatch')
class SettingsView(View):
    """
    A settings view where the logged-in user can change his settings.
    """
    template_name = 'account/settings.html'

    @cached_property
    def last_intro_mod(self) -> Union[IntroductionModification, None]:
        """
        Return the :model:`forum_base.IntroductionModification` for the
        user.

        Return `None` if none exists.
        """
        try:
            return self.request.user.introductionmodification
        except IntroductionModification.DoesNotExist:
            return None

    def get(self, request: WSGIRequest):
        """
        Serving HTTP GET.
        """
        return render(
            request=request, template_name=self.template_name, context={
                'intro_mod_form': IntroductionModificationForm(
                    instance=self.last_intro_mod),
                'settings_form': SettingsForm(instance=request.user.settings)})

    def post(self, request: WSGIRequest):
        """
        Try to authenticate the user.
        """
        intro_mod_form = IntroductionModificationForm(
            data=request.POST, instance=self.last_intro_mod)
        settings_form = SettingsForm(
            data=request.POST, instance=request.user.settings)
        messages = []
        if intro_mod_form.is_valid() and settings_form.is_valid():
            settings_form.save()
            messages.append(_('Settings successfully saved.'))
            if intro_mod_form.instance.id is None:
                # New instance, fill necessary data
                intro_mod_form.user = request.user
            intro_mod_form.save()
            messages.append(_(
                'Your new introductions have been saved successfully. '
                'However, they won\'t be visible until an admin approves '
                'them.'))
            # next_url = get_next_url(request)
            # return HttpResponseRedirect(redirect_to=next_url)
        # Invalid form
        return render(
            request=request, template_name=self.template_name, context={
                'messages': messages,
                'intro_mod_form': intro_mod_form})
