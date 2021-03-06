from binascii import unhexlify
from datetime import datetime
from hashlib import sha512
from io import BytesIO
from logging import Logger, getLogger
from re import compile as re_compile
from typing import Optional, Tuple
from urllib.parse import unquote

from django.conf import settings
from django.utils.functional import cached_property
from hyperlink import URL
from PIL import UnidentifiedImageError
from PIL.Image import Image as PilImage
from PIL.Image import open as image_open
from requests import get
from unidecode import unidecode

from forum.utils import get_random_safestring
from forum.utils.locking import MAX_FILENAME_SIZE
from forum.utils.pathlib import Path

from ..models import Image, ImageUrl, MissingImage
from .image import convert_image
from .paths import set_cdn_fileattrs

MISSING_ORIGSRC_LEN = MissingImage._meta.get_field('src').max_length
MAXLEN_IMAGEURL = ImageUrl._meta.get_field('orig_src').max_length
_LOGGER = getLogger(name=__name__)  # type: Logger
NOCONVERT_MIMETYPES = {
    'image/webp': dict(extension='webp', mode='RGBA'),
    # 'image/apng': dict(extension='png', mode='RGBA'),
    'image/png': dict(extension='png', mode='RGBA'),
    'image/gif': dict(extension='gif', mode='P'),
    'image/jpeg': dict(extension='jpg', mode='RGB'),
    'image/jp2': dict(extension='jp2', mode='RGBA')
}
# Don't download images with these hashes
CANCEL_HASH_SET = set(unhexlify(x) for x in (
    'cc2aa0e463e98c8f9a35ca3bfc244eb5c1426df254905286e34ac55956d8d02f'
    '63e0183406b6003f36096909bfcb82b8af68c6454ecf2f42cdbfaef92c9587bd',
))


class ImageAlreadyDownloadedError(Exception):
    'Raised when the image is already downloaded.'


class ImageMissingError(Exception):
    'Raised when the image is (already) missing.'


class CdnImageDownloader(object):
    'Downloading (and processing) an image for CDN storage.'
    _UNNECESSARY_FILENAME_PARTS = (
        'www.kepfeltoltes.hu',
        'www_kepfeltoltes_hu',
        'www-kepfeltoltes-hu',
        'wwwkepfeltolteshu',
        'wwwkepfeltoltes',
    )
    _FILE_SIMPLER_RE = re_compile(r'([^a-zA-Z0-9.\-]|-)+')
    _MAXLEN_FILENAME = min(
        Image._meta.get_field('cdn_path').max_length - len('2012/12/31/'),
        MAX_FILENAME_SIZE)

    def __init__(self, url: str, timestamp: Optional[datetime] = None):
        self._url_source = url
        self._timestamp = timestamp or datetime.now()

    @cached_property
    def _hash_source(self) -> str:
        'Return the SHA512 hash of the source URL.'
        return sha512(bytes(self._url_source, encoding='utf-8')).digest()

    @cached_property
    def _downloaded_content(self) -> Optional[BytesIO]:
        'Download the file and return its content in a `BytesIO`.'
        try:
            r = get(url=self._url_source, verify=False, timeout=10)
        except Exception as e:
            _LOGGER.error(msg=f'_downloaded_content - caught error: {e}')
            return None
        if r.status_code != 200:
            _LOGGER.error(
                msg='_downloaded_content - status_code for '
                f'{self._url_source!r} is {r.status_code}')
            return None
        return BytesIO(initial_bytes=r.content) or None

    @cached_property
    def _hash_downloaded(self) -> str:
        'Return the SHA512 hash of the downloaded content.'
        return sha512(self._downloaded_content.getvalue()).digest()

    def _get_extension_with_mimetype(self) -> Tuple[str, str]:
        """
        Return the enforced extension and mime type from the PIL Image,
        while optionally having it converted to another file type.
        """
        im = self._loaded_image
        mime_type = im.get_format_mimetype()
        if mime_type in NOCONVERT_MIMETYPES:
            return NOCONVERT_MIMETYPES[mime_type]['extension'], mime_type
        new_fp = BytesIO()
        output_image, save_kwargs, mime_type, extension = convert_image(
            image=im, size=im.size, do_watermark=False)
        if extension is None:
            # Convert everything else to WEBP
            extension = 'webp'
            mime_type = 'image/webp'
            save_kwargs.update(format='WEBP', minimize_size=True)
        output_image.save(fp=new_fp, **save_kwargs)
        self._loaded_image = output_image
        self._downloaded_content = new_fp
        del(self._hash_downloaded)
        return extension, mime_type

    @cached_property
    def _loaded_image(self) -> PilImage:
        'Return the memory loaded `PilImage`.'
        try:
            with image_open(self._downloaded_content) as fp:  # type: PilImage
                im = fp
                im.load()
                return im
        except UnidentifiedImageError:
            _LOGGER.debug(
                msg=f'{self._url_source!r} unidentified, marked as missing.')
            obj_missing = MissingImage.objects.create(
                src=self._url_source[:MISSING_ORIGSRC_LEN])
            raise ImageMissingError(obj_missing, True)

    def _get_filename_with_mimetype(self) -> Tuple[str, str]:
        """
        Return the filename for this download while converting the the
        downloaded content into one that can be stored and converted
        further later on.
        """
        enforced_extension, mime_type = self._get_extension_with_mimetype()
        url = URL.from_text(text=self._url_source)
        prefix = '.'.join(unquote(string=url.path[-1]).split('.')[:-1]) or \
            get_random_safestring(length=5)
        prefix = unidecode(string=prefix)
        for unnecessary_part in self._UNNECESSARY_FILENAME_PARTS:
            prefix = prefix.replace(unnecessary_part, '')
        prefix = self._FILE_SIMPLER_RE.sub('-', prefix).strip('-')
        prefix = prefix[:self._MAXLEN_FILENAME - len(enforced_extension) - 1]
        return '.'.join([prefix, enforced_extension]), mime_type

    def _get_stored_filename(self, abs_path: Path) -> str:
        'Return the final filename part of the fully stored CDN path.'
        filename = abs_path.name
        while True:
            if not abs_path.exists():
                break
            if len(filename) >= MAX_FILENAME_SIZE - 9:
                filename = filename[9:]
            filename = '-'.join((get_random_safestring(length=8), filename))
            abs_path = abs_path.parent.joinpath(filename)
        while True:
            temp_path = abs_path.parent.joinpath(get_random_safestring())
            if not temp_path.exists():
                break
        temp_path.write_bytes(data=self._downloaded_content.getvalue())
        set_cdn_fileattrs(path=temp_path)
        temp_path.rename(target=abs_path)
        _LOGGER.debug(msg=f'Stored {self._url_source!r} into {abs_path!r}.')
        return abs_path.name

    def _get_saved_cdn_metapath(self, filename: str) -> Path:
        'Return the saved CDN metapath.'
        cdn_metaparts = (
            *self._timestamp.date().isoformat().split('-'), filename)
        size_root = settings.CDN['PATH_SIZES']['downloaded']  # type: Path
        abs_path = size_root.ensure_parentdirs(
            relative_path=cdn_metaparts,
            mode=settings.CDN['POSIXFLAGS']['mode_dir'],
            gid=settings.CDN['POSIXFLAGS']['gid'])
        filename = self._get_stored_filename(abs_path=abs_path)
        return Path(*cdn_metaparts).parent.joinpath(filename)

    def _get_cdn_image(self) -> Image:
        'Return a previously or newly created `Image`.'
        # This can modify self._downloaded_content, keep it here!
        filename, mime_type = self._get_filename_with_mimetype()
        cdn_image = Image.objects.filter(
            file_hash=self._hash_downloaded).first()  # type: Image
        if cdn_image:
            _LOGGER.debug(
                msg=f'{self._url_source!r} already downloaded to '
                f'{cdn_image.cdn_path!r}.')
            return cdn_image
        cdn_metapath = self._get_saved_cdn_metapath(filename=filename)
        return Image.objects.create(
            mime_type=mime_type, cdn_path=cdn_metapath,
            file_hash=self._hash_downloaded, width=self._loaded_image.width,
            height=self._loaded_image.height)

    def _do_preliminary_checks(self):
        'Do preliminary checks, to raise exceptions for early exits.'
        obj_missing = MissingImage.objects.filter(
            src=self._url_source[:MISSING_ORIGSRC_LEN]).first()
        if obj_missing:
            _LOGGER.debug(msg=f'{self._url_source!r} already missing.')
            raise ImageMissingError(obj_missing, False)
        stored_url = ImageUrl.objects.select_related('image').filter(
            src_hash=self._hash_source).first()  # type: ImageUrl
        if stored_url:
            _LOGGER.debug(
                msg=f'{self._url_source!r} already downloaded to'
                f'{stored_url.image.cdn_path!r}.')
            raise ImageAlreadyDownloadedError(stored_url.image)
        if self._downloaded_content is None or \
                self._hash_downloaded in CANCEL_HASH_SET:
            _LOGGER.debug(msg=f'Added {self._url_source!r} as missing.')
            obj_missing = MissingImage.objects.create(
                src=self._url_source[:MISSING_ORIGSRC_LEN])
            raise ImageMissingError(obj_missing, True)

    def process(self) -> Optional[Image]:
        'Download and process, return an `Image`, or raise exceptions.'
        self._do_preliminary_checks()
        cdn_image = self._get_cdn_image()
        ImageUrl.objects.create(
            image=cdn_image, orig_src=self._url_source[:MAXLEN_IMAGEURL],
            src_hash=self._hash_source)
        return cdn_image
