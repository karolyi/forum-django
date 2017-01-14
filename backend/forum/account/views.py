
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
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

    def get(self, request: WSGIRequest):
        """
        Serving HTTP GET.
        """
        return render(
            request=request, template_name=self.template_name, context={
                'intro_mod_form': IntroductionModificationForm(
                    user=request.user),
                'settings_form': SettingsForm(instance=request.user)})

    def post(self, request: WSGIRequest):
        """
        Try to authenticate the user.
        """
        intro_mod_form = IntroductionModificationForm(
            data=request.POST, user=request.user)
        settings_form = SettingsForm(
            data=request.POST, instance=request.user)
        if intro_mod_form.is_valid() and settings_form.is_valid():
            settings_form.save()
            messages.success(request=request, message=_(
                'Settings successfully saved.'))
            if intro_mod_form.instance.pk is None:
                # New instance, fill necessary data
                intro_mod_form.instance.user = request.user
            if intro_mod_form.has_changed():
                intro_mod_form.save()
                messages.info(request=request, message=_(
                    'Your new introductions have been saved successfully. '
                    'However, they won\'t be visible until an admin approves '
                    'them.'))
            return HttpResponseRedirect(
                redirect_to=reverse('forum:account:settings'))
        # Invalid form
        return render(
            request=request, template_name=self.template_name, context={
                'intro_mod_form': intro_mod_form,
                'settings_form': settings_form})
