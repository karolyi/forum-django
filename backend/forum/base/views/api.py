from decimal import Decimal

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models.aggregates import Avg, Count
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from forum.base.utils.home import collect_topic_page
from forum.rating.models import UserRating
from forum.rest_api.exceptions import NotProduceable
from forum.rest_api.utils.common import cast_to_set_of_slug
from forum.utils.decorators import logged_in_or_404
from forum.utils.mixins import JsonResponseMixin

from ..choices import LIST_TOPIC_TYPE, TOPIC_TYPE_ARCHIVED
from ..models import User


class UserSlugsView(JsonResponseMixin):
    'View to serve a JSON response of the requested user slugs.'

    def _gather_userinfo(self, set_slug: set) -> dict:
        'Collect and return the userinfos first.'
        qs_settings = User.objects.filter(slug__in=set_slug).only(
            'slug', 'quote', 'is_banned', 'is_staff', 'is_superuser')
        if qs_settings.count() != len(set_slug):
            raise Http404
        dict_result = dict()
        for user in qs_settings:
            dict_result[user.slug] = {
                'quote': user.quote, 'isSuperuser': user.is_superuser,
                'isStaff': user.is_staff, 'isBanned': user.is_banned,
                # Default values here
                'rating': dict(avg=0, count=0),
            }
        return dict_result

    def _equip_ratings(self, dict_result: dict):
        'Modify the result in place with the ratings.'
        qs_ratings = UserRating.objects.filter(
            ratee__slug__in=dict_result.keys(), is_enabled=True).values(
            'ratee__slug').annotate(Avg('value'), Count('value'))
        for rating in qs_ratings:
            user_slug = rating['ratee__slug']
            rating_avg = round(Decimal(rating['value__avg']), 2)
            dict_result[user_slug]['rating']['avg'] = rating_avg
            dict_result[user_slug]['rating']['count'] = rating['value__count']

    def get_json_data(self, context: dict) -> dict:
        'Collect the data here.'
        try:
            set_slug = cast_to_set_of_slug(str_input=context['slug_list'])
        except NotProduceable as exc:
            self.status_code = exc.status_code
            return dict(status='error', message=exc.message)
        dict_result = self._gather_userinfo(set_slug=set_slug)
        self._equip_ratings(dict_result=dict_result)
        return dict_result


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
            'topic_list': qs_topics_archived})


@require_GET  # Checked second
@logged_in_or_404  # Checked first
def v1_find_users_by_name(request: WSGIRequest) -> JsonResponse:
    """
    Find users by a string their name contains.
    Return the found users in JSON formatted as a select2 result.
    """
    name_contains = request.GET.get('name_contains')
    if name_contains is None or len(name_contains) < 2:
        # Nothing to search for or not enough data
        raise Http404
    try:
        page_id = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    users = User.objects.filter(username__icontains=name_contains).only(
        'slug', 'username').exclude(slug=request.user.slug)
    paginator = Paginator(object_list=users, per_page=10)
    try:
        page = paginator.page(number=page_id)
    except EmptyPage:
        raise Http404
    result = {
        'pagination': {
            'more': page.has_next()}}
    result['results'] = [{'id': x.slug, 'text': x.username} for x in page]
    return JsonResponse(data=result)
