from decimal import Decimal

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import InvalidPage
from django.db.models.aggregates import Avg, Count
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from forum.base.utils.home import collect_topic_page
from forum.rating.models import UserRating
from forum.rest_api.exceptions import NotProduceable
from forum.rest_api.utils import cast_to_set_of_slug

from ..choices import LIST_TOPIC_TYPE, TOPIC_TYPE_ARCHIVED
from ..models import Settings


def v1_user_short(request: WSGIRequest, slug_list: str) -> JsonResponse:
    """
    Serve some short information about the requested user IDs such as
    quotes, and staff/superuser status and received ratings.
    """
    try:
        set_slug = cast_to_set_of_slug(slug_list)
    except NotProduceable as exc:
        return exc.json_response()
    qs_settings = Settings.objects.filter(
        slug__in=set_slug).select_related('user').only(
        'slug', 'quote', 'is_banned', 'user__is_staff', 'user__is_superuser')
    if qs_settings.count() != len(set_slug):
        raise Http404
    dict_result = {}
    dict_id_slug = {}
    for model_settings in qs_settings:
        dict_id_slug[model_settings.user_id] = model_settings.slug
        dict_result[model_settings.slug] = {
            'quote': model_settings.quote,
            'isSuperuser': model_settings.user.is_superuser,
            'isStaff': model_settings.user.is_staff,
            'isBanned': model_settings.is_banned,
            'rating': {
                # Default values here
                'avg': 0,
                'count': 0
            }
        }
    qs_ratings = UserRating.objects.filter(
        ratee_id__in=dict_id_slug.keys(), is_enabled=True).values(
        'ratee').annotate(Avg('value'), Count('value'))
    for rating in qs_ratings:
        user_id = rating['ratee']
        user_slug = dict_id_slug[user_id]
        rating_avg = round(Decimal(rating['value__avg']), 2)
        dict_result[user_slug]['rating']['avg'] = rating_avg
        dict_result[user_slug]['rating']['count'] = rating['value__count']
    return JsonResponse(dict_result)


def v1_topic_list_page(request: WSGIRequest) -> HttpResponse:
    """
    Render a HTML for a topic page, requested by the paginating script.
    """
    # Sanitize input
    topic_type = request.GET.get('topic_type')
    if request.GET.get('topic_type') not in LIST_TOPIC_TYPE:
        raise Http404
    try:
        page_id = int(request.GET.get('page_id'))
    except (TypeError, ValueError):
        raise Http404
    try:
        topic_list = collect_topic_page(
            request=request, topic_type=topic_type, page_id=page_id,
            force=True)
    except InvalidPage:
        raise Http404
    return render(
        request=request,
        template_name='default/base/render-topic-group-page-inside.html',
        context={
            'topic_list': topic_list
        })


def v1_archived_topics_start(request: WSGIRequest) -> HttpResponse:
    """
    Render the starter HTML for the archived topics, including the
    first page of the topic listing section, and the paginator wrapper.
    """
    qs_topics_archived = collect_topic_page(
        request=request, topic_type=TOPIC_TYPE_ARCHIVED, page_id=1, force=True)
    return render(
        request=request,
        template_name='default/base/topic-archived-start.html',
        context={
            'topic_list': qs_topics_archived
        })
