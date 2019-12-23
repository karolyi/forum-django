from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    BooleanField, CharField, DateField, DateTimeField,
    PositiveSmallIntegerField, TextField)
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from forum.base.models import Topic, User
from forum.utils import slugify

from .choices import EVENT_RESPONSES


class Event(Model):
    'A stored event.'

    class Meta(object):
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return self.name

    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=100,
        populate_from=('name',), unique=True, slugify_function=slugify)
    name = CharField(verbose_name=_('Name'), max_length=150)
    place = CharField(verbose_name=_('Place'), max_length=100)
    owner = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('Owner'))
    topic = ForeignKey(
        to=Topic, on_delete=CASCADE, verbose_name=_('Related topic'), null=True)
    date_start = DateField(verbose_name=_('Start date'))
    date_end = DateField(verbose_name=_('End date'))
    is_enabled = BooleanField(default=False)
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
    images = ManyToManyField(
        'forum_cdn.Image',
        verbose_name=_('Images in this event\'s description'))


class EventResponse(Model):
    'An response for a given event.'

    class Meta(object):
        verbose_name = _('Event response')
        verbose_name_plural = _('Event responses')
        unique_together = (('event', 'invitee'),)

    def __str__(self):
        return _(
            'Event response for \'{event}\', from {invitee}: '
            '{response}').format(
            event=self.event, invitee=self.invitee,
            response=self.get_response_display())

    event = ForeignKey(to=Event, on_delete=CASCADE, verbose_name=_('Event'))
    last_modified = DateTimeField(
        auto_now=True, verbose_name=_('Last modified at'))
    inviter = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Inviter'), null=True,
        related_name='event_sharings')
    invitee = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Invitee'),
        related_name='event_responses')
    status = PositiveSmallIntegerField(
        verbose_name=_('Response'), choices=EVENT_RESPONSES,
        default=EVENT_RESPONSES[0][0])
