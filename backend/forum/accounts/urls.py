from django.conf.urls import include, url

from .views import LoginView

urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(), name='login'),
    url('^', include('django.contrib.auth.urls')),
]
