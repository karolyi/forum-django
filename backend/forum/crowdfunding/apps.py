from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CrowdFundingConfig(AppConfig):
    name = 'forum.crowdfunding'
    verbose_name = _('Forum: Crowd Funding')
    label = 'forum_crowdfunding'
