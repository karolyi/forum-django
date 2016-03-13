from django.utils.translation import ugettext_lazy as _

TOPIC_TYPE_NORMAL = 'normal'
TOPIC_TYPE_HIGHLIGHTED = 'highlighted'
TOPIC_TYPE_ARCHIVED = 'archived'

TOPIC_TYPE_CHOICES = (
    (TOPIC_TYPE_NORMAL, _('Normal')),
    (TOPIC_TYPE_ARCHIVED, _('Archived')),
    (TOPIC_TYPE_HIGHLIGHTED, _('Highlighted'))
)
