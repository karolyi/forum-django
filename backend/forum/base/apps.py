from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'base'
    verbose_name = _('Base')
    label = 'base'
