from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'forum.base'
    verbose_name = _('Forum: Base')
    label = 'forum_base'
