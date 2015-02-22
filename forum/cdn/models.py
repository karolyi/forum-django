from django.db import models
from django.utils.translation import ugettext_lazy as _


class Image(models.Model):

    """Model for the saved images"""

    comment = models.ManyToManyField(
        'base.Comment', null=None, default=1, verbose_name=_('Found in comment'))
    orig_src = models.URLField(
        verbose_name=_('Original source'), max_length=256)
    mime_type = models.CharField(verbose_name=_('Mime type'), max_length=100)
    cdn_path = models.CharField(verbose_name=_('Path in CDN'), max_length=256)
    file_hash = models.CharField(verbose_name=_('File hash'), max_length=200)


class MissingImage(models.Model):

    """Model for the missing images, so they don't need to be downloaded again"""

    src = models.URLField(verbose_name=_('Original source'), max_length=256)
