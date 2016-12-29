from django.conf import settings
from django.contrib.auth import login as login_django
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import ForumAuthForm


class LoginView(TemplateView):
    """
    Dealing with login.
    """
    template_name = 'registration/login.html'

    def get(self, request):
        """
        Render the login form as empty.
        """
        return render(
            request=request, template_name=self.template_name, context={
                'auth_form': ForumAuthForm(is_autofocus=True)})

    def post(self, request):
        """
        Try to authenticate the user.
        """
        auth_form = ForumAuthForm(
            request=request, data=request.POST, is_autofocus=True)
        if auth_form.is_valid():
            next_url = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
            login_django(request, auth_form.get_user())
            return HttpResponseRedirect(redirect_to=next_url)
        # Invalid login
        return render(
            request=request, template_name=self.template_name, context={
                'auth_form': auth_form})
