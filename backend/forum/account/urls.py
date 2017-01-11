from django.conf.urls import include, url

from .views import LoginView, SettingsView, logout

urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(), name='login'),
    url(r'^logout/$', view=logout, name='logout'),
    url(r'^settings/$', view=SettingsView.as_view(), name='settings'),
    url('^', include('django.contrib.auth.urls')),
]
