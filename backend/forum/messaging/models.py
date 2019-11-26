from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    BooleanField, CharField, DateTimeField,
    PositiveSmallIntegerField, TextField)
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _

from forum.base.models import User
from forum.cdn.models import Image

from .choices import MESSAGE_STATUSES


class Mail(Model):
    'Private messaging, mail-like functionality.'

    class Meta(object):
        verbose_name = _('Mail message')
        verbose_name_plural = _('Mail messages')

    def __str__(self):
        return _('Mail message of user {recipient} from user {sender}').format(
            sender=self.sender, recipient=self.recipient)

    # The collation for thread_id is binary, see the initial migration.
    thread_id = CharField(
        verbose_name=_('Thread ID'), max_length=10, null=True)
    sender = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Sender'),
        related_name='inbox_sender')
    recipient = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Recipient'),
        related_name='inbox_recipient')
    created_at = DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    opened_at = DateTimeField(null=True, verbose_name=_('Read at'))
    status = PositiveSmallIntegerField(
        verbose_name=_('Status'), choices=MESSAGE_STATUSES,
        default=MESSAGE_STATUSES[0][0])
    is_forwarded = BooleanField(
        verbose_name=_('Is forwarded'), default=False)
    is_retained_sender = BooleanField(
        verbose_name=_('Retained in sender\'s outbox'), default=False)
    is_retained_recipient = BooleanField(
        verbose_name=_('Retained in recipient\'s inbox'), default=False)
    sender_deleted = BooleanField(
        verbose_name=_('Sender deleted it in outbox'), default=False)
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
    images = ManyToManyField(
        to=Image, verbose_name=_('Images in this mail message'))


class GlobalMessage(Model):
    'A global message shown instantaneously for logged-in users.'

    class Meta(object):
        verbose_name = _('Global message')
        verbose_name_plural = _('Global messages')

    def __str__(self):
        return _(
            'Global message created by user {user} at {created_at}').format(
            user=self.user, created_at=self.created_at)

    user = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('Created by'))
    created_at = DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    is_enabled = BooleanField(verbose_name=_('Is enabled'))
    subject = CharField(verbose_name=_('Subject'), max_length=100)
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
    images = ManyToManyField(
        to=Image, verbose_name=_('Images in this global message'))
