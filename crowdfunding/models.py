from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models import Topic
from crowdfunding.choices import STATUS_CHOICES


class Project(models.Model):

    """
    A project for which users can apply for.
    """

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        return self.name

    name = models.CharField(verbose_name=_('Name'), max_length=50)
    owner = models.ForeignKey(User, verbose_name=_('Owner'))
    last_updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Last updated at'))
    ends_at = models.DateTimeField(verbose_name=_('Ends at'))
    related_topic = models.ForeignKey(
        Topic, verbose_name=_('Related topic'), null=True, default=None)
    status = models.PositiveSmallIntegerField(
        verbose_name=_('Status'), choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0])
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))


class ProjectBacker(models.Model):

    """
    A backer of a project.
    """

    class Meta:
        verbose_name = _('Project backer')
        verbose_name_plural = _('Project backers')
        unique_together = (('project', 'user'),)

    def __str__(self):
        return self.user

    project = models.ForeignKey(Project, verbose_name=_('Project'))
    user = models.ForeignKey(User, verbose_name=_('Backer'))
    last_updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('Last updated at'))
    content_html = models.TextField(verbose_name=_('HTML content'))
    content_md = models.TextField(verbose_name=_('Markdown content'))
