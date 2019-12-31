from django.conf.urls import url
from django.urls.conf import path

from .views.frontend import (
    TopicCommentListingView, TopicExpandRepliesUpRecursive, TopicListView,
    expand_comments_down, expand_comments_up)

urlpatterns = [
    path(route=r'', view=TopicListView.as_view(), name='topic-listing'),
    path(
        route='topic/<slug:topic_slug>/',
        view=TopicCommentListingView.as_view(), name='topic-comment-listing'),
    path(
        route='topic/<slug:topic_slug>/<int:comment_id>/',
        view=TopicCommentListingView.as_view(), name='topic-comment-listing'),
    path(
        route='comments-up-recursive/<slug:topic_slug>/<int:comment_id>'
        '/<int:scroll_to_id>/', view=TopicExpandRepliesUpRecursive.as_view(),
        name='comments-up-recursive'),
    url(regex=r'^comments-up/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=expand_comments_up, name='comments-up'),
    url(regex=r'^comments-down/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=expand_comments_down, name='comments-down'),
]
