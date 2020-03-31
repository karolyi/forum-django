from typing import Optional

from django.conf import settings
from django.core.paginator import Page, Paginator

from forum.base.models import Topic
from forum.utils.wsgi import ForumWSGIRequest

from ..choices import TOPIC_TYPE_ARCHIVED


def _get_topics_per_page(request: ForumWSGIRequest) -> int:
    'Return the shown topics per page for a user.'
    topics_per_page = request.session.get('topics-per-page')
    if type(topics_per_page) is int:
        return topics_per_page
    request.session['topics-per-page'] = settings.PAGINATOR_TOPICS_PER_PAGE
    return settings.PAGINATOR_TOPICS_PER_PAGE


def collect_topic_page(
        request: ForumWSGIRequest, topic_type: str, page_id: int = 1,
        force: bool = False) -> Optional[Page]:
    """
    Collect and return topic list for the home view, `None` when nothing
    selected.

    `force` signals that even if the user has disabled the expanding
    of archived topics in their settings, we want to forcibly load
    those.
    """
    if topic_type == TOPIC_TYPE_ARCHIVED and not force:
        if request.user.is_anonymous or not request.user.expand_archived:
            # AnonymousUser does not have settings, return empty,
            # or doesn't expand archived topics
            return
    search_kwargs = dict(is_enabled=True, type=topic_type)
    if not request.user.is_staff and not request.user.is_superuser:
        # Only list topics that are visible to the user
        search_kwargs['is_staff_only'] = False
    qs_topics = Topic.objects.filter(**search_kwargs).select_related(
        'last_comment__user')
    topics_per_page = _get_topics_per_page(request)
    paginator = Paginator(object_list=qs_topics, per_page=topics_per_page)
    page = paginator.page(number=page_id)
    return page
