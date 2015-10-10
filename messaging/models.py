from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from messaging.choices import MESSAGE_STATUSES


class Mail(models.Model):

    class Meta:
        verbose_name = _('Mail message')
        verbose_name_plural = _('Mail messages')

    def __str__(self):
        return _('Mail message of user %(recipient)s from user %(sender)s' % {
            'sender': self.sender,
            'recipient': self.recipient,
        })

    # The collation for thread_id is binary, see the initial migration.
    thread_id = models.CharField(
        verbose_name=_('Thread ID'), max_length=10, null=True)
    sender = models.ForeignKey(
        User, verbose_name=_('Sender'), related_name='inbox_sender')
    recipient = models.ForeignKey(
        User, verbose_name=_('Recipient'), related_name='inbox_recipient')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    opened_at = models.DateTimeField(null=True, verbose_name=_('Read at'))
    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'), choices=MESSAGE_STATUSES,
        default=MESSAGE_STATUSES[0][0])
    is_forwarded = models.BooleanField(
        verbose_name=_('Is forwarded'), default=False)
    is_retained_sender = models.BooleanField(
        verbose_name=_('Retained in sender\'s outbox'), default=False)
    is_retained_recipient = models.BooleanField(
        verbose_name=_('Retained in recipient\'s outbox'), default=False)
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))
