from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import AutoSlugField

from base.models import Topic
from event.choices import EVENT_RESPONSES


class Event(models.Model):

    """
    A stored event.
    """

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return self.name

    name = models.CharField(verbose_name=_('Name'), max_length=150)
    place = models.CharField(verbose_name=_('Place'), max_length=100)
    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=100,
        populate_from=('name',), unique=True)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))
    topic = models.ForeignKey(
        Topic, verbose_name=_('Related topic'), null=True)
    date_start = models.DateField(verbose_name=_('Start date'))
    date_end = models.DateField(verbose_name=_('End date'))
    is_enabled = models.BooleanField(default=False)
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))


class Response(models.Model):

    """
    An response for a given event.
    """

    class Meta:
        verbose_name = _('Event invitation')
        verbose_name_plural = _('Event Invitations')
        unique_together = (('event', 'invitee'),)

    def __str__(self):
        return _(
            'Event invitation for \'%(event)s\', response from %(invitee)s: '
            '%(response)s' % {
                'event': self.event,
                'invitee': self.invitee,
                'response': self.get_response_display()
            })

    event = models.ForeignKey(Event, verbose_name=_('Event'))
    inviter = models.ForeignKey(
        User, verbose_name=_('Inviter'), null=True,
        related_name='event_sharings')
    invitee = models.ForeignKey(
        User, verbose_name=_('Invitee'), related_name='event_responses')
    response = models.PositiveSmallIntegerField(
        verbose_name=_('Response'), choices=EVENT_RESPONSES,
        default=EVENT_RESPONSES[0][0])