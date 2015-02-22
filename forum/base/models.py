from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Comments(models.Model):

    """Essential comment class"""

    user = models.ForeignKey(User, verbose_name=_('The commenter user'))
    topic = models.ForeignKey('Topics', verbose_name=_('Commented in topic'))
    moved_from = models.ForeignKey(
        'Topics', blank=True, default=None, related_name='moved_from',
        verbose_name=_('Comment moved from topic'), on_delete=models.SET_DEFAULT)
    time = models.DateTimeField(auto_now=True, verbose_name=_('Commented at'))
    number = models.IntegerField(verbose_name=_('Comment number in topic'))
    voting_value = models.IntegerField(verbose_name=_('Value of up/downvotes'))
    prev_comment = models.ForeignKey(
        'self', verbose_name=_('Answered comment'), blank=True, default=None,
        on_delete=models.SET_DEFAULT)
    content = models.TextField(verbose_name=_('Content'))
    host = models.CharField(
        max_length=256, verbose_name=_('Host of the commenter'))
    ip = models.IPAddressField(verbose_name=_('IP of the commenter'))
    edits = models.ForeignKey('Edits', verbose_name=_('Edits'))
    unique_id = models.CharField(
        verbose_name=_('Obsolete unique ID'),
        null=False,
        default=0,
        max_length=20, unique=True)


class Edits(models.Model):

    """Comment edits"""

    timestamp = models.DateTimeField(
        auto_now=True, verbose_name=_('Edit timestamp'))
    diff = models.TextField(verbose_name=_('Diff of the previous version'))


class Topics(models.Model):

    """Essential topic class"""

    creator = models.ForeignKey(User, verbose_name=_('Topic creator'))
    html = models.CharField(max_length=256, verbose_name=_('HTML name'))
    text = models.CharField(max_length=256, verbose_name=_('Text name'))
    is_disabled = models.BooleanField(
        blank=False, default=True, verbose_name=_('Is topic disabled'))
    is_staff_only = models.BooleanField(
        blank=False, default=False, verbose_name=_('Is staff only'))
    is_voting_enabled = models.BooleanField(
        blank=False,
        default=True,
        verbose_name=_('Is voting enabled'))
    truncate_at = models.IntegerField(
        default=0,
        verbose_name=_('Max comment number to keep'))
    reply_to = models.ForeignKey(
        'self', blank=True, default=None, verbose_name=_('Reply to topic goes to'))
    last_updated = models.DateTimeField(
        auto_now=True, verbose_name=_('Last updated'))
    slug = models.SlugField(verbose_name=_('Topic slug'))
    comment_count = models.IntegerField(verbose_name=_('Comment count'))
    last_comment = models.ForeignKey(
        Comments, verbose_name=_('Last comment reference'))
    description = models.TextField(verbose_name=_('HTML description'))
