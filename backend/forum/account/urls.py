from django.conf.urls import include, url

from .views import LoginView, SettingsView, logout

urlpatterns = [
    url(regex=r'^login/$', view=LoginView.as_view(), name='login'),
    url(regex=r'^logout/$', view=logout, name='logout'),
    url(regex=r'^settings/$', view=SettingsView.as_view(), name='settings'),
    url(regex='^', view=include('django.contrib.auth.urls')),
]
