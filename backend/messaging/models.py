from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from messaging.choices import MESSAGE_STATUSES


class Mail(models.Model):

    """
    Private messaging, mail-like functionality.
    """

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
        verbose_name=_('Retained in recipient\'s inbox'), default=False)
    sender_deleted = models.BooleanField(
        verbose_name=_('Sender deleted it in outbox'), default=False)
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))
    images = models.ManyToManyField(
        'cdn.Image', verbose_name=_('Images in this mail message'))


class GlobalMessage(models.Model):

    """
    A global message shown instantaneously for logged-in users.
    """

    class Meta:
        verbose_name = _('Global message')
        verbose_name_plural = _('Global messages')

    def __str__(self):
        return _(
            'Global message created by user %(user)s at %(created_at)s' % {
                'user': self.user,
                'created_at': self.created_at
            })

    user = models.ForeignKey(User, verbose_name=_('Created by'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    is_enabled = models.BooleanField(verbose_name=_('Is enabled'))
    subject = models.CharField(verbose_name=_('Subject'), max_length=100)
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))
    images = models.ManyToManyField(
        'cdn.Image', verbose_name=_('Images in this global message'))
