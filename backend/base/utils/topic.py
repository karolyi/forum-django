from django.conf import settings
from django.core.paginator import Paginator
from django.http.response import Http404

from ..models import Comment, Topic


def _get_comments_per_page(request):
    """
    Return the shown topics per page for a user.
    """
    comments_per_page = request.session.get('comments_per_page')
    if comments_per_page is not None:
        return comments_per_page
    request.session['comments_per_page'] = \
        settings.PAGINATOR_MAX_COMMENTS_LISTED
    return settings.PAGINATOR_MAX_COMMENTS_LISTED


def _get_comment_pageid(qs_comments, comment_id, comments_per_page):
    """
    Get a page number for a given comment ID, so that we can display it
    on the right page.

    Return the page ID, raise `Http404` if the comment doesn't exist.
    """
    try:
        model_comment = qs_comments.get(id=comment_id)
    except Comment.DoesNotExist:
        # This comment does not exist here
        raise Http404
    amount_newer = qs_comments.filter(time__gt=model_comment.time).count()
    page_id = amount_newer // comments_per_page + 1
    return page_id


def list_comments(request, topic_slug, comment_id=None):
    """
    List a topic page with comments.

    Return the topic model and the requested page containing the
    `comment_id`.
    """
    search_kwargs_topic = {
        'slug': topic_slug,
        'is_staff_only': request.user.is_staff or request.user.is_superuser
    }
    try:
        model_topic = Topic.objects.get(**search_kwargs_topic)
    except Topic.DoesNotExist:
        raise Http404
    search_kwargs_comment = {
        'topic': model_topic
    }
    qs_comments = Comment.objects.filter(
        **search_kwargs_comment).order_by('-time')
    comments_per_page = _get_comments_per_page(request)
    page_id = 1
    if comment_id is not None:
        page_id = _get_comment_pageid(
            qs_comments, comment_id, comments_per_page)
    qs_comments = qs_comments.select_related(
        'topic', 'user', 'user__settings', 'prev_comment',
        'prev_comment__user', 'prev_comment__user__settings',
        'prev_comment__topic'
    ).prefetch_related(
        'reply_set', 'reply_set__user', 'reply_set__topic',
        'reply_set__user__settings')
    paginator = Paginator(qs_comments, comments_per_page)
    if not qs_comments.exists():
        raise Http404
    return model_topic, paginator.page(page_id)
