from __future__ import annotations

from hashlib import sha512
from json import loads
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
from django.db.models.manager import Manager
from django.db.models.signals import pre_delete
from django.utils.functional import cached_property
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _
from hyperlink import URL
from requests.api import get

from forum.utils.dbfields import Sha512Field
from forum.utils.locking import TempLock


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


class IframelyResponseManager(Manager):
    'Manager for `IframelyResponse`'
    _ORIGSRC_MAXLEN = 512
    _LOCKPREFIX = 'iframely-fetch-'

    @cached_property
    def _iframely_uri(self) -> URL:
        'Return a constructed `URL` where iframely is at.'
        conn = settings.IFRAMELY_CONNECTION
        return URL(
            scheme=conn.get('scheme', 'https'),
            host=conn.get('host', 'localhost'),
            path=conn.get('path', '/').lstrip('/').split('/'),
            port=conn.get('port', 443))

    @cached_property
    def _requests_authkwargs(self) -> dict:
        'Return the authentication kwargs for each iframely request.'
        auth = settings.IFRAMELY_CONNECTION.get('auth', {})
        if not auth or auth.get('mode') is None:
            # No authentication
            return dict()
        if auth.get('mode') == 'htaccess':
            return dict(
                auth=(auth.get('username', ''), auth.get('password', '')))
        return dict()

    def _get_and_store_url(
            self, url: str, src_hash: bytes) -> IframelyResponse:
        """
        Get, store and return a previously not found `IframelyResponse`
        for a `url`.
        """
        result = self.filter(src_hash=src_hash).first()
        if result:
            return result
        response = get(
            url=self._iframely_uri.replace(query=dict(uri=url)),
            **self._requests_authkwargs)
        return self.create(
            orig_src=url[:self._ORIGSRC_MAXLEN], src_hash=src_hash,
            accessed_at=localtime(), response_code=response.status_code,
            response_json=response.text)

    def get_for_url(self, url: str) -> IframelyResponse:
        'Return content for a URL.'
        hasher = sha512()
        hasher.update(url.encode('utf-8'))
        src_hash = hasher.digest()
        result = self.filter(src_hash=src_hash).first()
        if result:
            return result
        with TempLock(name=f'{self._LOCKPREFIX}{hasher.hexdigest()}'):
            return self._get_and_store_url(url=url, src_hash=src_hash)


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
        verbose_name=_('Original source'),
        max_length=IframelyResponseManager._ORIGSRC_MAXLEN)
    src_hash = Sha512Field(
        verbose_name=_('SHA512 hash of orig_src'), max_length=64)
    accessed_at = DateTimeField(verbose_name=_('Accessed at'))
    response_code = PositiveSmallIntegerField(
        verbose_name=_('HTTP response code'))
    response_json = TextField(verbose_name=_('JSON response'))

    objects = IframelyResponseManager()

    def __str__(self) -> str:
        return self.orig_src

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} '
            f'{self.response_code}: {self.orig_src!r}>')

    @cached_property
    def loaded_json(self) -> dict:
        'Load and return the parsed JSON.'
        return loads(self.response_json)
