from django.db import models
from django.utils.translation import ugettext_lazy as _
from forum.base.models import User


class CommentVote(models.Model):

    class Meta(object):
        verbose_name = _('Comment vote')
        verbose_name_plural = _('Comment votes')
        unique_together = (('comment', 'user'),)

    def __str__(self):
        return _('{value} on comment {comment}').format(
            value=self.value, comment=self.comment)

    comment = models.ForeignKey(
        'forum_base.Comment', verbose_name=_('Comment'))
    user = models.ForeignKey(User, verbose_name=_('User'))
    value = models.SmallIntegerField(verbose_name=_('Value'))


class UserRating(models.Model):

    """
    A rating of a user from another user.
    """

    class Meta(object):
        verbose_name = _('User rating')
        verbose_name_plural = _('User ratings')

    def __str__(self):
        return _(
            '{value} on user {ratee} from user {rater}').format(
            value=self.value, ratee=self.ratee, rater=self.rater)

    is_enabled = models.BooleanField(
        verbose_name=_('Is approved'), default=False)
    ratee = models.ForeignKey(
        User, verbose_name=_('Ratee'), related_name='ratee')
    rater = models.ForeignKey(
        User, verbose_name=_('Rater'), related_name='rater')
    value = models.SmallIntegerField(verbose_name=_('Value'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))
