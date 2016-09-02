from rest_api.exceptions import NotProduceable
from rest_api.utils import cast_to_set_of_slug
from base.models import Settings
from django.http.response import HttpResponse, JsonResponse, Http404


def v1_user_short(request, slug_list):
    """
    Serve some short information about the requested user IDs such as
    quotes, and staff/superuser status.
    """
    try:
        set_slug = cast_to_set_of_slug(slug_list)
    except NotProduceable as exc:
        return exc.json_response()
    qs_settings = Settings.objects.filter(
        slug__in=set_slug).select_related('user').only(
        'quote', 'is_banned', 'user__is_staff', 'user__is_superuser')
    if qs_settings.count() != len(set_slug):
        raise Http404
    dict_result = {}
    for model_settings in qs_settings:
        dict_result[model_settings.slug] = {
            'quote': model_settings.quote,
            'isSuperuser': model_settings.user.is_superuser,
            'isStaff': model_settings.user.is_staff,
            'isBanned': model_settings.is_banned,
        }
    return JsonResponse(dict_result)
