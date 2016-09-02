from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'rest_api'
    verbose_name = _('REST API backend')
    label = 'rest_api'
