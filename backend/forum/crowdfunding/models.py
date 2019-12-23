from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    CharField, DateTimeField, PositiveSmallIntegerField, TextField)
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from forum.base.models import Topic, User
from forum.utils import slugify

from .choices import STATUS_CHOICES


class Project(Model):
    'A project for which users can apply.'

    class Meta(object):
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.name

    slug = AutoSlugField(
        verbose_name=_('Slug'), null=False, max_length=50,
        populate_from=('name',), unique=True, slugify_function=slugify)
    name = CharField(verbose_name=_('Name'), max_length=255)
    owner = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('Owner'))
    last_updated_at = DateTimeField(
        auto_now=True, verbose_name=_('Last updated at'))
    ends_at = DateTimeField(verbose_name=_('Ends at'))
    related_topic = ForeignKey(
        to=Topic, on_delete=CASCADE, verbose_name=_('Related topic'),
        null=True, default=None)
    status = PositiveSmallIntegerField(
        verbose_name=_('Status'), choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0])
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
    images = ManyToManyField(
        'forum_cdn.Image',
        verbose_name=_('Images in this project description'))


class ProjectBacker(Model):
    'A backer of a project.'

    class Meta(object):
        verbose_name = _('Project backer')
        verbose_name_plural = _('Project backers')
        unique_together = (('project', 'user'),)

    def __str__(self):
        return self.user

    project = ForeignKey(
        to=Project, on_delete=CASCADE, verbose_name=_('Project'))
    user = ForeignKey(to=User, on_delete=CASCADE, verbose_name=_('Backer'))
    last_updated_at = DateTimeField(
        auto_now=True, verbose_name=_('Last updated at'))
    content_html = TextField(verbose_name=_('HTML content'))
    content_md = TextField(verbose_name=_('Markdown content'))
    images = ManyToManyField(
        'forum_cdn.Image', verbose_name=_('Images in this backer\'s message'))
