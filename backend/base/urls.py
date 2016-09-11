from django.conf.urls import url

from .views.frontend import topic_listing, topic_comment_listing

urlpatterns = [
    url(r'^$', topic_listing, name='topic-listing'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/$', topic_comment_listing,
        name='topic-comment-listing'),
    url(r'^topic/(?P<topic_slug>[a-z0-9-]+)/(?P<comment_id>\d+)/$',
        topic_comment_listing, name='topic-comment-listing'),
]
