from base.choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from base.utils.home import collect_topic_page
from base.utils.topic import list_comments
from django.shortcuts import render


def topic_listing(request):
    """
    Main entry page, with the topic listings.
    """
    request_context = {
        'topics_highlighted': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_HIGHLIGHTED, page_id=1),
        'topics_normal': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_NORMAL, page_id=1),
        'topics_archived': collect_topic_page(
            request=request, topic_type=TOPIC_TYPE_ARCHIVED, page_id=1),
    }
    return render(
        request=request, template_name='default/base/topic-listing.html',
        context=request_context)


def topic_comment_listing(request, topic_slug, comment_id=None):
    """
    List a certain topic.
    """
    model_topic, page_comments = list_comments(
        request=request, topic_slug=topic_slug, comment_id=comment_id)
    return render(
        request=request,
        template_name='default/base/topic-comment-listing.html',
        context={
            'page_comments': page_comments,
            'model_topic': model_topic,
            'comment_id': comment_id,
            'topic_slug': topic_slug,
        })
