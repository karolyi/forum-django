from django.conf.urls import url
from base.views.api import v1_user_short

urlpatterns = [
    url('^v1/user-short/(?P<slug_list>[a-z0-9-,]+)/$',
        v1_user_short, name='v1-user-short')
]
