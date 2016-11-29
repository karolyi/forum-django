from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from forum.base.models import Topic
from forum.utils import slugify


class Question(models.Model):

    """
    A poll question.
    """

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __str__(self):
        return self.text

    text = models.CharField(verbose_name=_('Text'), max_length=150)
    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=50,
        populate_from=('text',), unique=True, slugify_function=slugify)
    topic = models.ForeignKey(
        Topic, verbose_name=_('In topic'), null=True, default=None)
    created_by = models.ForeignKey(User, verbose_name=_('Created by'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Created at'))
    is_enabled = models.BooleanField(verbose_name=_('Enabled'), default=False)


class Choice(models.Model):

    """
    A poll choice.
    """

    class Meta:
        verbose_name = _('Choice')
        verbose_name_plural = _('Choices')

    def __str__(self):
        return _('%(text)s of question \'%(question)s\'') % {
            'question': self.question,
            'text': self.text}

    question = models.ForeignKey(Question, verbose_name=_('Question'))
    text = models.CharField(verbose_name=_('Text'), max_length=150)
    votes = models.PositiveIntegerField(verbose_name=_('Vote count'))
    order = models.PositiveSmallIntegerField(verbose_name=_('Order ID'))


class Vote(models.Model):

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        unique_together = (('user', 'question'),)

    def __str__(self):
        return _('\'%(user)s\' to Choice \'%(choice)s\'') % {
            'user': self.user,
            'choice': self.choice
        }

    user = models.ForeignKey(User, verbose_name=_('User'))
    question = models.ForeignKey(Question, verbose_name=_('Question'))
    choice = models.ForeignKey(Choice, verbose_name=_('Choice'))
    last_modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Last modified at'))
