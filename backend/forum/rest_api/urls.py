from django.conf.urls import re_path
from django.urls.conf import path

from forum.base.views.api import (
    ArchivedTopicsStartView, TopicListPageView, UserSlugsView,
    v1_find_users_by_name)
from forum.cdn.views.imager_api import ResizeImageView

from .views.md_helper import md_parser

urlpatterns_api = [
    path(
        route='v1/user-short/<slug_list>/', view=UserSlugsView.as_view(),
        name='v1-user-short'),
    re_path(
        route=r'^v1/topic-list-page/', view=TopicListPageView.as_view(),
        name='v1-topic-list-page'),
    re_path(
        route=r'^v1/archived-topics-start/',
        view=ArchivedTopicsStartView.as_view(),
        name='v1-archived-topics-start'),
    re_path(
        route=r'v1/imager/resize/(?P<img_path>.*)$',
        view=ResizeImageView.as_view(), name='v1-imager-resize'),
    re_path(
        route=r'^v1/find-users-by-name/', view=v1_find_users_by_name,
        name='v1-find-users-by-name'),
    re_path(route=r'^v1/md-parser/', view=md_parser, name='md-parser'),
]
