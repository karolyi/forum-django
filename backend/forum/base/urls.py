from django.conf.urls import url
from django.urls.conf import path

from .views.frontend import (
    TopicCommentListingView, TopicExpandCommentsDownView,
    TopicExpandCommentsUpView, TopicExpandRepliesUpRecursive, TopicListView)

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
        view=TopicExpandCommentsUpView.as_view(), name='comments-up'),
    url(regex=r'^comments-down/(?P<topic_slug>[a-z0-9-]+)/'
        r'(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        view=TopicExpandCommentsDownView.as_view(), name='comments-down'),
]
