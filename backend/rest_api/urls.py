from django.conf.urls import url
from base.views.api import v1_user_short, v1_topic_list_page

urlpatterns = [
    url('^v1/user-short/(?P<slug_list>[a-z0-9-,]+)/$',
        v1_user_short, name='v1-user-short'),
    url('^v1/topic-list-page/', v1_topic_list_page, name='v1-topic-list-page')
]
