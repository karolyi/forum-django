from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PollConfig(AppConfig):
    name = 'forum.poll'
    verbose_name = _('Forum: Polls')
    label = 'forum_poll'
