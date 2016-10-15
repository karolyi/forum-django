from django.conf.urls import url

from .views.frontend import (
    expand_comments_down, expand_comments_up, expand_comments_up_recursive,
    topic_comment_listing, topic_listing, jinja_test)

urlpatterns = [
    url(r'^$', jinja_test, name='topic-listing'),
    # url(r'^$', topic_listing, name='topic-listing'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/$', topic_comment_listing,
        name='topic-comment-listing'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/(?P<comment_id>\d+)/$',
        topic_comment_listing, name='topic-comment-listing'),
    url(r'^comments-up-recursive/(?P<topic_slug>[a-z0-9-]+)/'
        '(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        expand_comments_up_recursive, name='comments-up-recursive'),
    url(r'^comments-up/(?P<topic_slug>[a-z0-9-]+)/'
        '(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        expand_comments_up, name='comments-up'),
    url(r'^comments-down/(?P<topic_slug>[a-z0-9-]+)/'
        '(?P<comment_id>\d+)/(?P<scroll_to_id>\d+)/$',
        expand_comments_down, name='comments-down'),
]
