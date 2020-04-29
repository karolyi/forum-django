import os

from django.conf import settings
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, FilePathField, URLField
from django.db.models.fields.related import ForeignKey
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _


def cdn_delete_file(sender, instance, *args, **kwargs):
    abs_path = settings.PATH_CDN_ROOT.joinpath(instance.cdn_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)


class Image(Model):
    'The saved image files.'

    class Meta(object):
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    mime_type = CharField(verbose_name=_('Mime type'), max_length=100)
    cdn_path = FilePathField(
        path=settings.PATH_CDN_ROOT, verbose_name=_('Path in CDN'),
        max_length=191, unique=True)
    file_hash = CharField(
        verbose_name=_('File SHA512 hash'), max_length=128, unique=True)

    def __str__(self):
        return self.cdn_path


pre_delete.connect(cdn_delete_file, sender=Image)


class ImageUrl(Model):
    'The already downloaded image URLs.'

    class Meta(object):
        verbose_name = _('ImageUrl')
        verbose_name_plural = _('ImageUrls')

    def __str__(self):
        return self.orig_src

    image = ForeignKey(
        to=Image, on_delete=CASCADE, verbose_name=_('The CDN file'))
    orig_src = URLField(
        verbose_name=_('Original source'), max_length=512)
    src_hash = CharField(
        verbose_name=_('SHA512 hash of orig_src'), max_length=128, unique=True)


class MissingImage(Model):
    """
    The missing images, so they don't need to be downloaded again.
    """

    class Meta(object):
        verbose_name = _('Missing Image')
        verbose_name_plural = _('Missing Images')

    src = URLField(
        verbose_name=_('Original source'), max_length=191, db_index=True,
        unique=True)
