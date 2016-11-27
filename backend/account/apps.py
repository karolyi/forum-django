from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = _('Account')
    label = 'account'
