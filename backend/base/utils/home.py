from base.models import Topic
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator

from ..choices import TOPIC_TYPE_ARCHIVED


def _get_topics_per_page(request):
    """
    Return the shown topics per page for a user.
    """
    topics_per_page = request.session.get('topics_per_page')
    if topics_per_page is not None:
        return topics_per_page
    request.session['topics_per_page'] = settings.TOPICS_PER_PAGE
    return settings.TOPICS_PER_PAGE


def collect_topic_page(request, topic_type, page_id=1, force=False):
    """
    Collect topic list for the home view.

    `force` signals that even if the user has disabled the expanding
    of archived topics in their settings, we want to forcibly load
    those.
    """
    if topic_type == TOPIC_TYPE_ARCHIVED and not force:
        if isinstance(request.user, AnonymousUser):
            # AnonymousUser does not have settings
            return []
        if not request.user.settings.expand_archived:
            return []

    search_kwargs = {
        'is_enabled': True,
        'is_staff_only': request.user.is_staff,
    }
    search_kwargs['type'] = topic_type
    qs_topics = Topic.objects.filter(**search_kwargs).select_related(
        'last_comment', 'last_comment__user', 'last_comment__user__settings'
    ).only(
        'name_text', 'comment_count', 'last_comment__user__username',
        'last_comment__time')
    topics_per_page = _get_topics_per_page(request)
    paginator = Paginator(qs_topics, per_page=topics_per_page)
    return paginator.page(page_id)
