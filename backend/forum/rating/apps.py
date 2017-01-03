from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RatingConfig(AppConfig):
    name = 'forum.rating'
    verbose_name = _('Forum: Ratings')
    label = 'forum_rating'
