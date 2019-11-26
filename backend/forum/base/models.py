from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_DEFAULT, SET_NULL
from django.db.models.fields import (
    BooleanField, CharField, DateTimeField, GenericIPAddressField,
    IntegerField, PositiveIntegerField, SmallIntegerField, TextField)
from django.db.models.fields.related import (
    ForeignKey, ManyToManyField, OneToOneField)
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from forum.utils import slugify

from .choices import COMMENT_VOTE_HIDE_CHOICES, TOPIC_TYPE_CHOICES


class User(AbstractUser):
    """
    An object representing the user's settings.
    """

    class Meta:
        verbose_name = _('User setting')
        verbose_name_plural = _('User settings')
        ordering = ['username']

    slug = AutoSlugField(
        verbose_name=_('Slug of the user'), max_length=50, unique=True,
        populate_from='username', slugify_function=slugify, null=False,
        primary_key=True)
    last_global_read = PositiveIntegerField(
        verbose_name=_('Last global message ID read'), default=0)
    received_comment_vote_sum = IntegerField(
        verbose_name=_('Summary received votes value on comments'), default=0)
    received_comment_vote_count = PositiveIntegerField(
        verbose_name=_('Summary received votes count on comments'), default=0)
    comment_vote_hide_limit = IntegerField(
        default=-5, verbose_name=_('Hide comments under this vote value'),
        choices=COMMENT_VOTE_HIDE_CHOICES, help_text=_(
            'If a comment gets voted down under the selected value here, it '
            'gets completely hidden.'))
    quote = CharField(
        max_length=256, verbose_name=_('Chosen quote'), help_text=_(
            'Quote (visible in the tooltip of the username)'), blank=True)
    max_comments_per_day = IntegerField(
        verbose_name=_('Maximum allowed comments per day'), default=-1)
    comment_count = PositiveIntegerField(
        verbose_name=_('Comment count'), default=0)
    invitations_today = PositiveIntegerField(
        verbose_name=_('Sent invitations today'), default=0)
    invited_by = ForeignKey(
        to='self', on_delete=CASCADE, related_name='invited_user_setting_set',
        null=True, default=None, verbose_name=_('Invited by'))
    invitations_success = PositiveIntegerField(
        verbose_name=_('Successful invitations'), default=0)
    pw_reminders_today = PositiveIntegerField(
        verbose_name=_('Password reminders sent today'), default=0)
    used_skin = CharField(
        max_length=256, verbose_name=_('Used skin name'), default='default')
    introduction_md_all = TextField(
        verbose_name=_('Introduction for everybody (MD)'),
        help_text=_('Introduction in Markdown format (visible for everyone)'),
        default='')
    introduction_md_reg = TextField(
        verbose_name=_('Introduction for registered users (MD)'), help_text=_(
            'Introduction in Markdown format (visible for registered users '
            'only)'),
        default='')
    introduction_md_friends = TextField(
        verbose_name=_('Introduction for friended users (MD)'), help_text=_(
            'Introduction in Markdown format (visible only for users marked '
            'as friends)'),
        default='')
    introduction_html_all = TextField(
        verbose_name=_('Introduction for everybody (HTML)'), help_text=_(
            'Introduction in HTML format (visible for everyone)'),
        default='')
    introduction_html_reg = TextField(
        verbose_name=_('Introduction for registered users (HTML)'),
        help_text=_(
            'Introduction in HTML format (visible for registered users '
            'only)'),
        default='')
    introduction_html_friends = TextField(
        verbose_name=_('Introduction for friended users (HTML)'), help_text=_(
            'Introduction in HTML format (visible only for users marked as '
            'friends)'),
        default='')
    picture_emails = CharField(
        max_length=256, verbose_name=_(
            'Email addresses used for image upload'
            ' separated with semicolons (;)'), default='')
    ignored_users = ManyToManyField(
        'self', related_name='ignored_by',
        verbose_name=_('List of ignored users'),
        help_text=_('An ignored user\'s posts are invisible when added here.'),
        symmetrical=False, blank=True)
    friended_users = ManyToManyField(
        'self', verbose_name=_('Friended users'), related_name='friended_by',
        help_text=_(
            'The users who will see the part of the profile which is only '
            'visible for friended users.'),
        symmetrical=False, blank=True)
    uses_auto_bookmarks = BooleanField(
        default=False, verbose_name=_('Use automatic bookmark placement'),
        help_text=_(
            'When checked, the previously set bookmarks will automatically '
            'update to the newest seen comment in the topic pages as they are '
            'listed.'))
    mails_own_topic_comments = BooleanField(
        default=False, verbose_name=_(
            'Receive mails from comments in own topic'), help_text=_(
            'Receive email alerts if someone posts a comment in a created '
            'topic.'))
    mails_replies_topic = BooleanField(
        default=True, verbose_name=_('Receive mails from comment replies'),
        help_text=_(
            'Receive email alerts from replies to posted comments.'))
    mails_moderation_topic = BooleanField(
        default=True, verbose_name=_('Receive mails from moderation'),
        help_text=_(
            'Receive emails when an administrator takes a moderation action '
            '(e.g. edit, deletion, move) on the a posted comment.'))
    mails_messages = BooleanField(
        default=True, verbose_name=_('Receive mails from messages'),
        help_text=_(
            'Receive email alerts when a new private message arrives.'))
    show_replies_comment = BooleanField(
        default=True, verbose_name=_('Show replies on comments'))
    show_relations = BooleanField(
        default=True, verbose_name=_('Show user relations'))
    is_banned = BooleanField(
        default=False, verbose_name=_('User is banned'))
    separate_bookmarked_topics = BooleanField(
        default=True, verbose_name=_('Show bookmarked topics separated'),
        help_text=_(
            'Split the normal topic view to topics with set bookmarks and '
            'topics with none set.'))
    show_outsiders = BooleanField(
        default=True, verbose_name=_('Show not-logged-in users'))
    has_chat_enabled = BooleanField(
        default=True, verbose_name=_('Enable chat'), help_text=_(
            'Show the chat on the main page when logged in.'))
    is_approved = BooleanField(
        default=False, verbose_name=_('Is approved by admins'))
    expand_archived = BooleanField(
        default=False, verbose_name=_('Expand archived topics'), help_text=_(
            'Don\'t hide archived topics on the main page.'))
    images = ManyToManyField(
        'forum_cdn.Image',
        verbose_name=_('Images in this user\'s descriptions'))


User.ignored_users.through.__str__ = \
    lambda x: '{from_u} ignores {to_u}'.format(
        from_u=x.from_user, to_u=x.to_user)
User.friended_users.through.__str__ = \
    lambda x: '{from_u} befriended {to_u}'.format(
        from_u=x.from_user, to_u=x.to_user)


class Topic(Model):
    'Essential topic class.'

    class Meta(object):
        ordering = ['-last_comment__time', 'name_text']

    def __str__(self):
        return self.name_text

    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=100,
        populate_from=('name_text',), unique=True, slugify_function=slugify,
        primary_key=True)
    creator = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Creator'))
    name_html = CharField(max_length=256, verbose_name=_('HTML name'))
    name_text = CharField(max_length=256, verbose_name=_('Text name'))
    is_enabled = BooleanField(
        default=False, verbose_name=_('Is enabled'))
    is_staff_only = BooleanField(
        default=False, verbose_name=_('Is staff only'))
    is_voting_enabled = BooleanField(
        default=True, verbose_name=_('Is voting enabled'))
    type = CharField(
        verbose_name=_('Topic type'), max_length=20,
        choices=TOPIC_TYPE_CHOICES, default=TOPIC_TYPE_CHOICES[0][0])
    truncate_at = SmallIntegerField(
        null=True, verbose_name=_('Max comment number to keep'))
    reply_to = ForeignKey(
        to='self', on_delete=SET_NULL, null=True, default=None,
        verbose_name=_('Reply to topic goes to'))
    comment_count = PositiveIntegerField(
        verbose_name=_('Comment count'), default=0)
    last_comment = ForeignKey(
        to='Comment', on_delete=SET_NULL,
        verbose_name=_('Last comment reference'), null=True,
        related_name='last_comment')
    description = TextField(verbose_name=_('Description'))
    images = ManyToManyField(
        'forum_cdn.Image', verbose_name=_('Images in this topic description'))


class Comment(Model):
    """
    Essential comment class.

    The hostname is obsoleted, but since there's no stable way to get
    IPs from hostnames, we store it. It was stored in the previous
    version like that.
    """

    class Meta(object):
        ordering = ('-time',)
        index_together = (
            ('topic', 'time'),
        )

    def __str__(self):
        return str(_(
            '#{number} of \'{topic}\' (ID {id})'.format(
                number=self.number, topic=self.topic, id=self.id)))

    user = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('The commenter user'))
    topic = ForeignKey(to=Topic, on_delete=CASCADE, verbose_name=_('Topic'))
    moved_from = ForeignKey(
        to=Topic, on_delete=SET_DEFAULT, null=True, default=None,
        related_name='moved_from', verbose_name=_('Moved from'))
    time = DateTimeField(
        # auto_now_add=True,
        verbose_name=_('Commented at'))
    number = PositiveIntegerField(
        verbose_name=_('Comment number in topic'))
    voting_value = SmallIntegerField(
        verbose_name=_('Value of up/downvotes'))
    prev_comment = ForeignKey(
        to='self', on_delete=SET_DEFAULT, related_name='reply_set',
        verbose_name=_('Replied comment'), null=True, default=None)
    # FOR HTML ESCAPING IN MARKDOWN
    # https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated
    content_md = TextField(verbose_name=_('Markdown content'))
    content_html = TextField(verbose_name=_('HTML content'))
    host = CharField(
        max_length=256, verbose_name=_('Host of the commenter (old)'))
    ip = GenericIPAddressField(
        verbose_name=_('IP of the commenter'), null=False, blank=False)
    unique_id = CharField(
        verbose_name=_('Obsolete unique ID'),
        default=0,
        max_length=20, unique=True)
    images = ManyToManyField(
        'forum_cdn.Image', verbose_name=_('Images in this comment'))


class Edit(Model):
    'Comment edits.'

    comment = ForeignKey(
        to=Comment, on_delete=CASCADE, verbose_name=_('Edited comment'),
        null=False)
    edited_by = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Edited by'), null=False)
    timestamp = DateTimeField(
        auto_now_add=True, verbose_name=_('Edit timestamp'), null=False)
    reason = CharField(
        verbose_name=_('Reason for editing'), max_length=50, null=False,
        default='')
    diff = TextField(
        verbose_name=_('Diff of the previous version'), null=False)
    images = ManyToManyField(
        'forum_cdn.Image', verbose_name=_('Images in this edit'))


class IntroductionModification(Model):
    """
    When a user modifies his introductions, an admin has to approve it.

    Until that happens, this model stores the changes.
    """

    class Meta:
        verbose_name = _('Settings modification')
        verbose_name_plural = _('Settings modifications')

    def __str__(self):
        return str(self.user)

    user = OneToOneField(
        to=User, on_delete=CASCADE, verbose_name=_('Respective user'))
    quote = CharField(
        max_length=256, verbose_name=_('Chosen quote'), help_text=_(
            'Quote (visible in the tooltip of the username)'), blank=True)
    introduction_md_all = TextField(
        verbose_name=_('Introduction for everybody (MD)'),
        help_text=_('Introduction in Markdown format (visible for everyone)'))
    introduction_md_reg = TextField(
        verbose_name=_('Introduction for registered users (MD)'), help_text=_(
            'Introduction in Markdown format (visible for registered users '
            'only)'))
    introduction_md_friends = TextField(
        verbose_name=_('Introduction for friended users (MD)'), help_text=_(
            'Introduction in Markdown format (visible only for users marked '
            'as friends)'))
    images = ManyToManyField(
        'forum_cdn.Image',
        verbose_name=_('Images in this user\'s descriptions'))


class CommentBookmark(Model):

    """
    A set bookmark for a comment object. A bookmark notes where the user
    left off reading comments the last time.
    """

    class Meta(object):
        verbose_name = _('Comment bookmark')
        verbose_name_plural = _('Comment bookmarks')
        unique_together = (('user', 'topic'),)

    def __str__(self):
        return str(_('s(number)s in %(topic)s for %(user)s') % {
            'number': self.comment.number,
            'topic': self.topic,
            'user': self.user
        })

    user = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('User'))
    topic = ForeignKey(to=Topic, on_delete=CASCADE, verbose_name=_('Topic'))
    comment = ForeignKey(
        to=Comment, on_delete=CASCADE, verbose_name=_('Comment'))
    last_updated_at = DateTimeField(
        auto_now=True, verbose_name=_('Last updated at'))
