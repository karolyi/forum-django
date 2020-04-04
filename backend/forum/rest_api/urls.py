from django.conf.urls import url
from django.urls.conf import path

from forum.base.views.api import (
    ArchivedTopicsStartView, TopicListPageView, UserSlugsView,
    v1_find_users_by_name)

from .views.md_helper import md_parser

urlpatterns = [
    path(
        route='v1/user-short/<slug_list>/', view=UserSlugsView.as_view(),
        name='v1-user-short'),
    url(regex=r'^v1/topic-list-page/',
        view=TopicListPageView.as_view(), name='v1-topic-list-page'),
    url(regex=r'^v1/archived-topics-start/',
        view=ArchivedTopicsStartView.as_view(),
        name='v1-archived-topics-start'),
    url(regex=r'^v1/find-users-by-name/', view=v1_find_users_by_name,
        name='v1-find-users-by-name'),
    url(regex=r'^v1/md-parser/', view=md_parser, name='md-parser'),
]
