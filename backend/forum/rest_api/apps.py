from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'forum.rest_api'
    verbose_name = _('Forum: REST API backend')
    label = 'forum_rest_api'
