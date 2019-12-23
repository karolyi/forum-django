from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    BooleanField, CharField, DateTimeField, PositiveIntegerField,
    PositiveSmallIntegerField)
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from forum.base.models import Topic, User
from forum.utils import slugify


class Question(Model):
    'A poll question.'

    class Meta(object):
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return self.text

    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=50,
        populate_from=('text',), unique=True, slugify_function=slugify)
    text = CharField(verbose_name=_('Text'), max_length=255)
    topic = ForeignKey(
        to=Topic, on_delete=CASCADE, verbose_name=_('In topic'), null=True,
        default=None)
    created_by = ForeignKey(
        to=User, on_delete=CASCADE, verbose_name=_('Created by'))
    created_at = DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    is_enabled = BooleanField(verbose_name=_('Enabled'), default=False)


class Choice(Model):
    'A poll choice.'

    class Meta(object):
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')

    def __str__(self):
        return _('%(text)s of question \'%(question)s\'') % {
            'question': self.question,
            'text': self.text}

    question = ForeignKey(
        to=Question, on_delete=CASCADE, verbose_name=_('Question'))
    text = CharField(verbose_name=_('Text'), max_length=150)
    votes = PositiveIntegerField(verbose_name=_('Vote count'))
    order = PositiveSmallIntegerField(verbose_name=_('Order ID'))


class Vote(Model):
    'A casted vote on a poll.'

    class Meta(object):
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        unique_together = (('user', 'question'),)

    def __str__(self):
        return _('\'%(user)s\' to Choice \'%(choice)s\'') % {
            'user': self.user,
            'choice': self.choice
        }

    user = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('User'))
    question = ForeignKey(
        to=Question, on_delete=CASCADE, verbose_name=_('Question'))
    choice = ForeignKey(to=Choice, on_delete=CASCADE, verbose_name=_('Choice'))
    last_modified_at = DateTimeField(
        auto_now=True, verbose_name=_('Last modified at'))
