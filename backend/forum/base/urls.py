from django.conf.urls import url
from django.urls.conf import path

from .views.frontend import (
    TopicCommentListingView, TopicListView, expand_comments_down,
    expand_comments_up, expand_comments_up_recursive)

urlpatterns = [
    path(route=r'', view=TopicListView.as_view(), name='topic-listing'),
    path(
        route='topic/<slug:topic_slug>/',
        view=TopicCommentListingView.as_view(), name='topic-comment-listing'),
    path(
        route='topic/<slug:topic_slug>/<int:comment_id>/',
        view=TopicCommentListingView.as_view(), name='topic-comment-listing'),
    url(regex=r'^comments-up-recursive/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=expand_comments_up_recursive, name='comments-up-recursive'),
    url(regex=r'^comments-up/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=expand_comments_up, name='comments-up'),
    url(regex=r'^comments-down/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=expand_comments_down, name='comments-down'),
]
