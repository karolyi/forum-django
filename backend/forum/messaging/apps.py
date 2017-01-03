from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MessagingConfig(AppConfig):
    name = 'forum.messaging'
    verbose_name = _('Forum: Messaging')
    label = 'forum_messaging'
