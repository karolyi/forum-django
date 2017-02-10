from django.conf.urls import url
from forum.base.views.api import (
    v1_archived_topics_start, v1_find_users_by_name, v1_topic_list_page,
    v1_user_short)
from .views.md_helper import md_parser

urlpatterns = [
    url(r'^v1/user-short/(?P<slug_list>[a-z0-9-,]+)/$',
        v1_user_short, name='v1-user-short'),
    url(r'^v1/topic-list-page/',
        v1_topic_list_page, name='v1-topic-list-page'),
    url(r'^v1/archived-topics-start/',
        v1_archived_topics_start, name='v1-archived-topics-start'),
    url(r'^v1/find-users-by-name/', v1_find_users_by_name,
        name='v1-find-users-by-name'),
    url(r'^v1/md-parser/', md_parser, name='md-parser'),
]
