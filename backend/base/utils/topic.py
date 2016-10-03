from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http.response import Http404
from django.urls.base import reverse

from ..exceptions import HttpResponsePermanentRedirect
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


def _prefetch_for_comments(qs_comments):
    """
    Take a Django :model:`base.Comment` QuerySet and prefetch/select
    all related models for displaying their variables in the templates.

    In general, this caching speed up the comments page generation,
    sparing sometimes hundreds of lazily queried data.

    Return the `QuerySet` with the prefetch statements added.
    """
    return qs_comments.select_related(
        'topic', 'user', 'user__settings', 'prev_comment',
        'prev_comment__user', 'prev_comment__user__settings',
        'prev_comment__topic'
    ).prefetch_related(
        'reply_set', 'reply_set__user', 'reply_set__topic',
        'reply_set__user__settings')


def _expansion_sanitize(request, topic_slug, comment_id):
    """
    Sanitize the expansion parameters and check if a requested topic
    is available to the requesting user.

    Raise Http404 if not.

    Return the :model:`base.Comment` for further expansion, and the
    extra kwargs for the comment selection query (don't display comments
    that are in a topic not visible to the user).
    """
    # Get the requested comment (cast to int before)
    comment_id = int(comment_id)
    search_kwargs_comment = {
        'id': comment_id
    }
    if not request.user.is_staff and not request.user.is_superuser:
        search_kwargs_comment['topic__is_staff_only'] = False
    try:
        model_comment = Comment.objects.select_related(
            'topic').only('id', 'topic__slug').get(**search_kwargs_comment)
    except Comment.DoesNotExist:
        raise Http404
    del(search_kwargs_comment['id'])
    return model_comment, search_kwargs_comment


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
    }
    if not request.user.is_staff and not request.user.is_superuser:
        search_kwargs_topic['is_staff_only'] = False
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
            qs_comments, int(comment_id), comments_per_page)
    qs_comments = _prefetch_for_comments(qs_comments)
    paginator = Paginator(qs_comments, comments_per_page)
    if not qs_comments.exists():
        raise Http404
    return model_topic, paginator.page(page_id)


def replies_up_recursive(request, topic_slug, comment_id):
    """
    Expand comments in a thread upwards from a given comment ID
    recursively.

    Return the :model:`base.Topic` and QuerySet of expanded comments
    (time descending)  when successfully gathered them.

    Raise `HttpResponsePermanentRedirect` when the comment exists but
    is in another topic, `Http404` when not found.
    """
    # Get the requested comment
    model_comment, search_kwargs_comment = _expansion_sanitize(
        request=request, topic_slug=topic_slug, comment_id=comment_id)
    if model_comment.topic.slug != topic_slug:
        url = reverse(
            'base:comments-up-recursive',
            kwargs={
                'topic_slug': model_comment.topic.slug,
                'comment_id': model_comment.id,
                'scroll_to_id': model_comment.id})
        raise HttpResponsePermanentRedirect(url=url)
    set_comment_ids = set([model_comment.id])
    set_iteration_ids = set([model_comment.id])
    while True:
        search_kwargs_comment['prev_comment__in'] = set_iteration_ids
        qs_comments = Comment.objects.filter(
            **search_kwargs_comment).only('id').order_by()
        set_iteration_ids = set([x.id for x in qs_comments])
        if len(set_iteration_ids) == 0:
            # No more comments fetchable
            break
        set_comment_ids.update(set_iteration_ids)
    qs_comments = Comment.objects.filter(id__in=set_comment_ids)
    qs_comments = _prefetch_for_comments(qs_comments)
    return model_comment.topic, qs_comments


def replies_up(request, topic_slug, comment_id):
    """
    Expand comments in a thread upwards from a given comment ID.

    Return the :model:`base.Topic` and QuerySet of expanded comments
    (time descending)  when successfully gathered them.

    Raise `HttpResponsePermanentRedirect` when the comment exists but
    is in another topic, `Http404` when not found.
    """
    # Get the requested comment
    model_comment, search_kwargs_comment = _expansion_sanitize(
        request=request, topic_slug=topic_slug, comment_id=comment_id)
    if model_comment.topic.slug != topic_slug:
        url = reverse(
            'base:comments-up',
            kwargs={
                'topic_slug': model_comment.topic.slug,
                'comment_id': model_comment.id,
                'scroll_to_id': model_comment.id})
        raise HttpResponsePermanentRedirect(url=url)
    search_kwargs_replies = search_kwargs_comment.copy()
    search_kwargs_comment['id'] = model_comment.id
    search_kwargs_replies['prev_comment_id'] = model_comment.id
    qs_comments = Comment.objects.filter(
        Q(**search_kwargs_comment) | Q(**search_kwargs_replies))
    qs_comments = _prefetch_for_comments(qs_comments)
    return model_comment.topic, qs_comments


def prev_comments_down(request, topic_slug, comment_id):
    """
    Expand the previous comments in the thread along with the requested
    comment ID.

    Return the :model:`base.Topic` and QuerySet of expanded comments
    (time descending)  when successfully gathered them.

    Raise `HttpResponsePermanentRedirect` when the comment exists but
    is in another topic, `Http404` when not found.
    """
    # Get the requested comment
    model_comment, search_kwargs_comment = _expansion_sanitize(
        request=request, topic_slug=topic_slug, comment_id=comment_id)
    if model_comment.topic.slug != topic_slug:
        url = reverse(
            'base:comments-up-recursive',
            kwargs={
                'topic_slug': model_comment.topic.slug,
                'comment_id': model_comment.id,
                'scroll_to_id': model_comment.id})
        raise HttpResponsePermanentRedirect(url=url)
    set_comment_ids = set()
    last_id = model_comment.id
    while True:
        search_kwargs_comment['id'] = last_id
        set_comment_ids.add(last_id)
        try:
            model_comment_iter = Comment.objects.only(
                'id', 'prev_comment_id').get(**search_kwargs_comment)
        except Comment.DoesNotExist:
            # No such comment (or in a topic that's not visible)
            break
        if model_comment_iter.prev_comment_id is None:
            # This comment is the root comment, not a reply
            break
        last_id = model_comment_iter.prev_comment_id
    qs_comments = Comment.objects.filter(id__in=set_comment_ids)
    qs_comments = _prefetch_for_comments(qs_comments)
    return model_comment.topic, qs_comments
