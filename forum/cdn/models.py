from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Image(models.Model):

    """
    The saved image files
    """

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    comment = models.ManyToManyField(
        'base.Comment', null=False, verbose_name=_('Found in comment'))
    topic = models.ManyToManyField('base.Topic', null=False)
    mime_type = models.CharField(verbose_name=_('Mime type'), max_length=100)
    cdn_path = models.FilePathField(
        path=settings.PATH_CDN_ROOT, verbose_name=_('Path in CDN'),
        max_length=255, unique=True)
    file_hash = models.CharField(
        verbose_name=_('File SHA512 hash'), max_length=128, unique=True)

    def __str__(self):
        return self.cdn_path


class ImageUrl(models.Model):

    """
    The already downloaded image URLs
    """

    class Meta:
        verbose_name = _('ImageUrl')
        verbose_name_plural = _('ImageUrls')

    def __str__(self):
        return self.orig_src

    image = models.ForeignKey(
        'cdn.Image', verbose_name=_('The CDN file'))
    orig_src = models.URLField(
        verbose_name=_('Original source'), max_length=512, db_index=True,
        null=False)
    src_hash = models.CharField(
        verbose_name=_('SHA512 hash of orig_src'), max_length=128, unique=True,
        null=False)


class MissingImage(models.Model):

    """
    The missing images, so they don't need to be downloaded again
    """

    class Meta:
        verbose_name = _('Missing Image')
        verbose_name_plural = _('Missing Images')

    src = models.URLField(
        verbose_name=_('Original source'), max_length=255, db_index=True,
        unique=True)
