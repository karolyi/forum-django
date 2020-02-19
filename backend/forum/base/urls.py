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
        route='topic/<slug:topic_slug>/<int:comment_pk>/',
        view=TopicCommentListingView.as_view(), name='topic-comment-listing'),
    path(
        route='comments-up-recursive/<slug:topic_slug>/<int:comment_pk>'
        '/<int:scroll_to_pk>/', view=TopicExpandRepliesUpRecursive.as_view(),
        name='comments-up-recursive'),
    path(
        route=(
            'comments-up/<slug:topic_slug>/'
            '<int:comment_pk>/<int:scroll_to_pk>/'),
        view=TopicExpandCommentsUpView.as_view(), name='comments-up'),
    path(
        route=(
            'comments-down/<slug:topic_slug>/'
            '<int:comment_pk>/<int:scroll_to_pk>/'),
        view=TopicExpandCommentsDownView.as_view(), name='comments-down'),
]
