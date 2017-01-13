from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Page, Paginator
from forum.base.models import Topic

from ..choices import TOPIC_TYPE_ARCHIVED


def _get_topics_per_page(request: WSGIRequest) -> int:
    """
    Return the shown topics per page for a user.
    """
    topics_per_page = request.session.get('topics_per_page')
    if topics_per_page is not None:
        return topics_per_page
    request.session['topics_per_page'] = settings.PAGINATOR_MAX_PAGES_TOPICLIST
    return settings.PAGINATOR_MAX_PAGES_TOPICLIST


def collect_topic_page(
        request: WSGIRequest, topic_type: str, page_id: int=1,
        force: bool=False) -> Union[bool, Page]:
    """
    Collect topic list for the home view.

    `force` signals that even if the user has disabled the expanding
    of archived topics in their settings, we want to forcibly load
    those.
    """
    if topic_type == TOPIC_TYPE_ARCHIVED and not force:
        if isinstance(request.user, AnonymousUser):
            # AnonymousUser does not have settings, return False
            return False
        if not request.user.expand_archived:
            # Return False
            return False

    search_kwargs = {
        'is_enabled': True
    }
    if not request.user.is_staff and not request.user.is_superuser:
        # Only list topics that are visible to the user
        search_kwargs['is_staff_only'] = False
    search_kwargs['type'] = topic_type
    qs_topics = Topic.objects.filter(**search_kwargs).select_related(
        'last_comment', 'last_comment__user', 'last_comment__user'
    ).only(
        'name_text', 'comment_count', 'last_comment__user__username',
        'last_comment__time')
    topics_per_page = _get_topics_per_page(request)
    paginator = Paginator(qs_topics, per_page=topics_per_page)
    return paginator.page(page_id)
