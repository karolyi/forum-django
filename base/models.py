from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from base.choices import TOPIC_TYPE_CHOICES
from base.utils import slugify


class Comment(models.Model):

    """
    Essential comment class.

    The hostname is obsoleted, but since there's no stable way to get
    IPs from hostnames, we store it. It was stored in the previous
    version like that.
    """

    def __str__(self):
        return _('Comment of user %(user)s in \'%(topic)s\'' % {
            'user': self.user,
            'topic': self.topic
        })

    user = models.ForeignKey(User, verbose_name=_('The commenter user'))
    topic = models.ForeignKey('Topic', verbose_name=_('Commented in topic'))
    moved_from = models.ForeignKey(
        'Topic', null=True, default=None, related_name='moved_from',
        verbose_name=_('Comment moved from topic'),
        on_delete=models.SET_DEFAULT)
    time = models.DateTimeField(
        # auto_now_add=True,
        verbose_name=_('Commented at'))
    number = models.PositiveIntegerField(
        verbose_name=_('Comment number in topic'))
    voting_value = models.SmallIntegerField(
        verbose_name=_('Value of up/downvotes'))
    prev_comment = models.ForeignKey(
        'self', verbose_name=_('Answered comment'), null=True, default=None,
        on_delete=models.SET_DEFAULT)
    # FOR HTML ESCAPING IN MARKDOWN
    # https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated
    content_md = models.TextField(verbose_name=_('Markdown content'))
    content_html = models.TextField(verbose_name=_('HTML content'))
    host = models.CharField(
        max_length=256, verbose_name=_('Host of the commenter (old)'))
    ip = models.GenericIPAddressField(
        verbose_name=_('IP of the commenter'), null=False, blank=False)
    unique_id = models.CharField(
        verbose_name=_('Obsolete unique ID'),
        default=0,
        max_length=20, unique=True)


class Edit(models.Model):

    """
    Comment edits.
    """

    comment = models.ForeignKey(
        'Comment', verbose_name=_('Edited comment'), null=False)
    edited_by = models.ForeignKey(
        User, verbose_name=_('Edited by'), null=False)
    timestamp = models.DateTimeField(
        # auto_now_add=True,
        verbose_name=_('Edit timestamp'), null=False)
    reason = models.CharField(
        verbose_name=_('Reason for editing'), max_length=50, null=False,
        default='')
    diff = models.TextField(
        verbose_name=_('Diff of the previous version'), null=False)


class Topic(models.Model):

    """
    Essential topic class.
    """

    def __str__(self):
        return self.text_name

    creator = models.ForeignKey(User, verbose_name=_('Topic creator'))
    name_html = models.CharField(max_length=256, verbose_name=_('HTML name'))
    name_text = models.CharField(max_length=256, verbose_name=_('Text name'))
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
        choices=TOPIC_TYPE_CHOICES, default=TOPIC_TYPE_CHOICES[0][0])
    truncate_at = models.SmallIntegerField(
        null=True,
        verbose_name=_('Max comment number to keep'))
    reply_to = models.ForeignKey(
        'self', null=True, default=None, on_delete=models.SET_NULL,
        verbose_name=_('Reply to topic goes to'))
    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=100,
        populate_from=('text_name',), unique=True)
    comment_count = models.PositiveIntegerField(
        verbose_name=_('Comment count'), null=False, default=0)
    last_comment = models.ForeignKey(
        Comment, verbose_name=_('Last comment reference'), null=True,
        related_name='last_comment', on_delete=models.SET_NULL)
    description = models.TextField(verbose_name=_('Description'))


class Settings(models.Model):

    """
    An object represeting the user's settings.
    """

    def _my_slugify(user_instance):
        """
        Returns the username from the OneToOneField relation to User.
        """
        return slugify(user_instance.username)

    def __str__(self):
        return _('Settings for user %s' % self.user)

    user = models.OneToOneField(
        User, verbose_name=_('Respective user'), null=False)
    slug = AutoSlugField(
        verbose_name=_('Slug of the user'), max_length=50, unique=True,
        populate_from='user', slugify_function=_my_slugify, null=False)
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
    invitations_today = models.PositiveIntegerField(
        verbose_name=_('Sent invitations today'))
    invited_by = models.ForeignKey(
        User, related_name='invited_user_setting_set', null=True,
        default=None, verbose_name=_('Invited by'))
    invitations_success = models.PositiveIntegerField(
        verbose_name=_('Successful invitations'))
    pw_reminders_today = models.PositiveIntegerField(
        verbose_name=_('Password reminders sent today'))
    used_skin = models.CharField(
        max_length=256, verbose_name=_('Used skin name'))
    introduction_md_all = models.TextField(
        verbose_name=_('Introduction visible for everybody (Markdown)'))
    introduction_md_reg = models.TextField(
        verbose_name=_('Introduction visible for registered users (Markdown)'))
    introduction_md_friends = models.TextField(
        verbose_name=_('Introduction visible for friended users (Markdown)'))
    introduction_html_all = models.TextField(
        verbose_name=_('Introduction visible for everybody (HTML)'))
    introduction_html_reg = models.TextField(
        verbose_name=_('Introduction visible for registered users (HTML)'))
    introduction_html_friends = models.TextField(
        verbose_name=_('Introduction visible for friended users (HTML)'))
    picture_emails = models.CharField(
        max_length=256, verbose_name=_(
            'Email addresses used for image upload'
            ' separated with semicolon (;)'))
    ignored_users = models.ManyToManyField(
        User, related_name='ignored_users', null=False,
        verbose_name=_('List of ignored users'))
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