from django.conf.urls import url

from forum.base.views.api import (
    v1_archived_topics_start, v1_find_users_by_name, v1_topic_list_page,
    v1_user_short)

from .views.md_helper import md_parser

urlpatterns = [
    url(regex=r'^v1/user-short/(?P<slug_list>[a-z0-9-,]+)/$',
        view=v1_user_short, name='v1-user-short'),
    url(regex=r'^v1/topic-list-page/',
        view=v1_topic_list_page, name='v1-topic-list-page'),
    url(regex=r'^v1/archived-topics-start/',
        view=v1_archived_topics_start, name='v1-archived-topics-start'),
    url(regex=r'^v1/find-users-by-name/', view=v1_find_users_by_name,
        name='v1-find-users-by-name'),
    url(regex=r'^v1/md-parser/', view=md_parser, name='md-parser'),
]
