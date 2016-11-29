from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'forum.accounts'
    verbose_name = _('Forum: Accounts')
    label = 'forum_accounts'
