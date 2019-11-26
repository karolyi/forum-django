from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    BooleanField, DateTimeField, SmallIntegerField, TextField)
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _

from forum.base.models import Comment, User


class CommentVote(Model):
    'A vote on a comment.'

    class Meta(object):
        verbose_name = _('Comment vote')
        verbose_name_plural = _('Comment votes')
        unique_together = (('comment', 'user'),)

    def __str__(self):
        return _('{value} on comment {comment}').format(
            value=self.value, comment=self.comment)

    comment = ForeignKey(
        to=Comment, on_delete=CASCADE, verbose_name=_('Comment'))
    user = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('User'))
    value = SmallIntegerField(verbose_name=_('Value'))


class UserRating(Model):
    'A rating of a user from another user.'

    class Meta(object):
        verbose_name = _('User rating')
        verbose_name_plural = _('User ratings')

    def __str__(self):
        return _(
            '{value} on user {ratee} from user {rater}').format(
            value=self.value, ratee=self.ratee, rater=self.rater)

    is_enabled = BooleanField(
        verbose_name=_('Is approved'), default=False)
    ratee = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Ratee'),
        related_name='ratee')
    rater = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Rater'), related_name='rater')
    value = SmallIntegerField(verbose_name=_('Value'))
    created_at = DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
