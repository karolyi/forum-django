from base.models import Topic
from django.conf import settings
from django.core.paginator import Paginator


def _get_topics_per_page(request):
    """
    Return the shown topics per page for a user.
    """
    topics_per_page = request.session.get('topics_per_page')
    if topics_per_page is not None:
        return topics_per_page
    request.session['topics_per_page'] = settings.TOPICS_PER_PAGE
    return settings.TOPICS_PER_PAGE


def collect_topic_page(request, topic_type, page_id=1):
    """
    Collect topic list for the home view.
    """
    search_kwargs = {
        'is_enabled': True,
    }
    if not request.user.is_staff:
        search_kwargs['is_staff_only'] = False
    search_kwargs['type'] = topic_type
    qs_topics = Topic.objects.filter(**search_kwargs).select_related(
        'last_comment', 'last_comment__user', 'last_comment__user__settings'
    ).only(
        'name_text', 'comment_count', 'last_comment__user__username',
        'last_comment__time')
    topics_per_page = _get_topics_per_page(request)
    paginator = Paginator(qs_topics, per_page=topics_per_page)
    return paginator.page(page_id)
