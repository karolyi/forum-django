from django.conf.urls import include, url

from .views import LoginView, logout

urlpatterns = [
    url(r'^login/$', view=LoginView.as_view(), name='login'),
    url(r'^logout/$', view=logout, name='logout'),
    url('^', include('django.contrib.auth.urls')),
]
