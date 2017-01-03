from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EventConfig(AppConfig):
    name = 'forum.event'
    verbose_name = _('Forum: Events')
    label = 'forum_event'
