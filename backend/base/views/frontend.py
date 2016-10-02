from django.shortcuts import render

from ..choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from ..exceptions import HttpResponsePermanentRedirect
from ..utils.home import collect_topic_page
from ..utils.topic import list_comments, replies_up_recursive


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
            'comment_id': comment_id
        })


def expand_comments_up_recursive(
        request, topic_slug, comment_id, scroll_to_id):
    """
    Expand replies to a given comment, by expanding all that is a reply
    to the given comment upwards.
    """
    try:
        model_topic, qs_comments = replies_up_recursive(
            request=request, topic_slug=topic_slug, comment_id=comment_id)
    except HttpResponsePermanentRedirect as exc:
        return exc.http_response()
    return render(
        request=request, template_name='default/base/comments-expansion.html',
        context={
            'model_topic': model_topic,
            'comment_id': comment_id,
            'qs_comments': qs_comments,
            'scroll_to_id': scroll_to_id
        })
