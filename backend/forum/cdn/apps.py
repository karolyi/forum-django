from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CdnConfig(AppConfig):
    name = 'forum.cdn'
    verbose_name = _('Forum: CDN')
    label = 'forum_cdn'
