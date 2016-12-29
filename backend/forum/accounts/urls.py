from django.conf.urls import include, url
from django.contrib.auth.views import auth_login

from .forms import ForumAuthForm
from .views import login

urlpatterns = [
    url(r'^login/$', view=login, kwargs={
        'authentication_form': ForumAuthForm
    }, name='login'),
    url('^', include('django.contrib.auth.urls')),
]
