from pathlib import Path

from django.conf import settings
from django.db.models.base import Model
from django.db.models.constraints import UniqueConstraint
from django.db.models.deletion import CASCADE
from django.db.models.fields import (
    CharField, DateTimeField, FilePathField, PositiveIntegerField,
    PositiveSmallIntegerField, TextField, URLField)
from django.db.models.fields.related import ForeignKey
from django.db.models.indexes import Index
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _

from forum.utils.dbfields import Sha512Field


def cdn_delete_file(sender, instance, *args, **kwargs):
    for path_item in settings.CDN['PATH_SIZES'].values():  # type: Path
        size_path = path_item.joinpath(instance.cdn_path)
        if size_path.exists():
            size_path.unlink()
        # TODO: Remove directories


class Image(Model):
    'The saved image files.'

    class Meta(object):
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        constraints = (
            UniqueConstraint(fields=['file_hash'], name='filehash'),
        )

    mime_type = CharField(verbose_name=_('Mime type'), max_length=100)
    cdn_path = FilePathField(
        path=str(settings.CDN['PATH_ROOT']), verbose_name=_('Path in CDN'),
        max_length=191, unique=True)
    file_hash = Sha512Field(verbose_name=_('File SHA512 hash'), max_length=64)
    width = PositiveIntegerField(verbose_name=_('Width'))
    height = PositiveIntegerField(verbose_name=_('Height'))

    def __str__(self):
        return self.cdn_path


pre_delete.connect(cdn_delete_file, sender=Image)


class ImageUrl(Model):
    'The already downloaded image URLs.'

    class Meta(object):
        verbose_name = _('ImageUrl')
        verbose_name_plural = _('ImageUrls')
        constraints = (
            UniqueConstraint(fields=['src_hash'], name='srchash'),
        )

    def __str__(self):
        return self.orig_src

    image = ForeignKey(
        to=Image, on_delete=CASCADE, verbose_name=_('The CDN file'))
    orig_src = URLField(
        verbose_name=_('Original source'), max_length=512)
    src_hash = Sha512Field(
        verbose_name=_('SHA512 hash of orig_src'), max_length=64)


class MissingImage(Model):
    'The missing images, so they don\'t need to be downloaded again.'

    class Meta(object):
        verbose_name = _('Missing Image')
        verbose_name_plural = _('Missing Images')

    src = URLField(
        verbose_name=_('Original source'), max_length=191, db_index=True,
        unique=True)


class IframelyResponse(Model):
    'A response from iframely for a requested URL.'

    class Meta(object):
        verbose_name = _('ImageUrl')
        verbose_name_plural = _('ImageUrls')
        indexes = (
            Index(fields=['accessed_at'], name='accessedat'),
        )
        constraints = (
            UniqueConstraint(fields=['src_hash'], name='srchash'),
        )

    orig_src = URLField(
        verbose_name=_('Original source'), max_length=512)
    src_hash = Sha512Field(
        verbose_name=_('SHA512 hash of orig_src'), max_length=64)
    accessed_at = DateTimeField(verbose_name=_('Accessed at'))
    response_code = PositiveSmallIntegerField(
        verbose_name=_('HTTP response code'))
    response_json = TextField(verbose_name=_('JSON response'))
