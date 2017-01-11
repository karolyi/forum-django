from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'forum.account'
    verbose_name = _('Forum: Account')
    label = 'forum_account'
