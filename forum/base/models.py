from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from base.choices import TOPIC_STATUS_CHOICES


class Comment(models.Model):

    """Essential comment class"""

    user = models.ForeignKey(User, verbose_name=_('The commenter user'))
    topic = models.ForeignKey('Topic', verbose_name=_('Commented in topic'))
    moved_from = models.ForeignKey(
        'Topic', null=True, default=None, related_name='moved_from',
        verbose_name=_('Comment moved from topic'),
        on_delete=models.SET_DEFAULT)
    time = models.DateTimeField(auto_now=True, verbose_name=_('Commented at'))
    number = models.PositiveIntegerField(
        verbose_name=_('Comment number in topic'))
    voting_value = models.SmallIntegerField(
        verbose_name=_('Value of up/downvotes'))
    prev_comment = models.ForeignKey(
        'self', verbose_name=_('Answered comment'), null=True, default=None,
        on_delete=models.SET_DEFAULT)
    content = models.TextField(verbose_name=_('Content'))
    host = models.CharField(
        max_length=256, verbose_name=_('Host of the commenter (old)'))
    ip = models.GenericIPAddressField(
        verbose_name=_('IP of the commenter'), null=False, blank=False)
    unique_id = models.CharField(
        verbose_name=_('Obsolete unique ID'),
        default=0,
        max_length=20, unique=True)


class Edit(models.Model):

    """Comment edits"""

    comment = models.ForeignKey('Comment', verbose_name=_('Edited comment'))
    timestamp = models.DateTimeField(
        auto_now=True, verbose_name=_('Edit timestamp'))
    diff = models.TextField(verbose_name=_('Diff of the previous version'))


class Topic(models.Model):

    """Essential topic class"""

    creator = models.ForeignKey(User, verbose_name=_('Topic creator'))
    html_name = models.CharField(max_length=256, verbose_name=_('HTML name'))
    text_name = models.CharField(max_length=256, verbose_name=_('Text name'))
    is_disabled = models.BooleanField(
        null=False, default=True, verbose_name=_('Is topic disabled'))
    is_staff_only = models.BooleanField(
        null=False, default=False, verbose_name=_('Is staff only'))
    is_voting_enabled = models.BooleanField(
        null=False,
        default=True,
        verbose_name=_('Is voting enabled'))
    type = models.CharField(
        verbose_name=_('Topic type'), null=False, max_length=20,
        choices=TOPIC_STATUS_CHOICES, default=TOPIC_STATUS_CHOICES[0][0])
    truncate_at = models.SmallIntegerField(
        null=True,
        verbose_name=_('Max comment number to keep'))
    reply_to = models.ForeignKey(
        'self', null=True, default=None, on_delete=models.SET_NULL,
        verbose_name=_('Reply to topic goes to'))
    slug = AutoSlugField(
        verbose_name=_('Topic slug'), null=False, max_length=100,
        populate_from=('text',), unique=True)
    comment_count = models.PositiveIntegerField(
        verbose_name=_('Comment count'), null=False, default=0)
    last_comment = models.ForeignKey(
        Comment, verbose_name=_('Last comment reference'), null=True,
        related_name='last_comment', on_delete=models.SET_NULL)
    description = models.TextField(verbose_name=_('Description'))


class User(User):
    slug = AutoSlugField(
        verbose_name=_('Slug of the user'), max_length=50, unique=True,
        populate_from=('username',), null=False)
    last_global_read = models.PositiveIntegerField(
        verbose_name=_('Last global message ID read'))
    received_comment_vote_sum = models.IntegerField(
        verbose_name=_('Summary received votes value on comments'))
    received_comment_vote_count = models.PositiveIntegerField(
        verbose_name=_('Summary received votes count on comments'))
    comment_vote_hide_limit = models.IntegerField(
        default=-5, verbose_name=_('Hide comments under this vote value'))
    quote = models.CharField(
        max_length=256, verbose_name=_('Chosen quote (appears at username)'))
    max_comments_per_day = models.PositiveIntegerField(
        verbose_name=_('Maximum allowed comments per day'))
    comment_count = models.PositiveIntegerField(
        verbose_name=_('Comment count'))
    # todays_comment_count = models.PositiveIntegerField(
    #     verbose_name=_('Today\'s comment count'))
    invitations_today = models.PositiveIntegerField(
        verbose_name=_('Sent invitations today'))
    inviter = models.ForeignKey(
        'self', null=True, default=None, verbose_name=_('Invited by'))
    invitations_success = models.PositiveIntegerField(
        verbose_name=_('Successful invitations'))
    pw_reminders_today = models.PositiveIntegerField(
        verbose_name=_('Password reminders sent today'))
    used_skin = models.CharField(
        max_length=256, verbose_name=_('Used skin name'))
    introduction_all = models.TextField(
        verbose_name=_('Introduction visible for everybody'))
    introduction_reg = models.TextField(
        verbose_name=_('Introduction visible for registered users'))
    introduction_friends = models.TextField(
        verbose_name=_('Introduction visible for friended users'))
    picture_emails = models.CharField(
        max_length=256, verbose_name=_(
            'Email addresses used for image upload'
            ' separated with semicolon (;)'))
    ignored_users = models.ManyToManyField(
        'self', null=None, verbose_name=_('List of ignored users'))
    uses_auto_bookmarks = models.BooleanField(
        null=False, default=False,
        verbose_name=_('Use automatic bookmark placement'))
    mails_own_topic_comments = models.BooleanField(
        null=False, default=False,
        verbose_name=_('Receive mails from comments in own topic'))
    mails_replies_topic = models.BooleanField(
        null=False, default=True,
        verbose_name=_('Receive mails from comment replies'))
    mails_moderation_topic = models.BooleanField(
        null=False, default=True,
        verbose_name=_('Receive mails from moderation'))
    mails_messages = models.BooleanField(
        null=False, default=True,
        verbose_name=_('Receive mails from messages'))
    show_replies_comment = models.BooleanField(
        null=False, default=True, verbose_name=_('Show replies on comments'))
    show_relations = models.BooleanField(
        null=False, default=True, verbose_name=_('Show user relations'))
    is_banned = models.BooleanField(
        null=False, default=False, verbose_name=_('User is banned'))
    separate_bookmarked_topics = models.BooleanField(
        null=False, default=True,
        verbose_name=_('Show bookmarked topics separated'))
    show_outsiders = models.BooleanField(
        null=False, default=True, verbose_name=_('Show not-logged-in users'))
    has_chat_enabled = models.BooleanField(
        null=False, default=True, verbose_name=_('Enable chat'))
    is_approved = models.BooleanField(
        null=False, default=False, verbose_name=_('Is approved by admins'))
    expand_archived = models.BooleanField(
        null=False, default=False, verbose_name=_('Expand archived topics'))
