from datetime import datetime
from hashlib import sha512
from io import BytesIO
from logging import Logger, getLogger
from pathlib import Path
from re import compile as re_compile
from typing import Optional, Tuple

from django.utils.functional import cached_property
from hyperlink import URL
from PIL import UnidentifiedImageError
from PIL.Image import Image as PilImage
from PIL.Image import open as image_open
from requests import get
from unidecode import unidecode

from forum.utils import get_random_safestring
from forum.utils.locking import MAX_FILENAME_SIZE

from ..models import Image, ImageUrl, MissingImage
from .image import create_animated_gif, create_animated_webp
from .paths import get_path_with_ensured_dirs, set_cdn_fileattrs

MISSING_ORIGSRC_LEN = MissingImage._meta.get_field('src').max_length
MAXLEN_IMAGEURL = ImageUrl._meta.get_field('orig_src').max_length
_logger = getLogger(name=__name__)  # type: Logger
MIMETYPE_ASSIGNMENTS = {
    'image/webp': dict(extension='webp', mode='RGBA'),
    # 'image/apng': dict(extension='png', mode='RGBA'),
    'image/png': dict(extension='png', mode='RGBA'),
    'image/gif': dict(extension='gif', mode='P'),
    'image/jpeg': dict(extension='jpg', mode='RGB'),
    'image/jp2': dict(extension='jp2', mode='RGBA')
}
# Don't download images with these hashes
CANCEL_HASH_SET = set((
    'cc2aa0e463e98c8f9a35ca3bfc244eb5c1426df254905286e34ac55956d8d02f'
    '63e0183406b6003f36096909bfcb82b8af68c6454ecf2f42cdbfaef92c9587bd',
))


class ImageAlreadyDownloadedException(Exception):
    'Raised when the image is already downloaded.'


class ImageMissingException(Exception):
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
    _FILE_SIMPLER_RE = re_compile(r'[^a-zA-Z0-9.\-]+')

    def __init__(self, url: str, timestamp: Optional[datetime] = None):
        self._url_source = url
        self._timestamp = timestamp or datetime.now()

    @cached_property
    def _hash_source(self) -> str:
        'Return the SHA512 hash of the source URL.'
        return sha512(bytes(self._url_source, encoding='utf-8')).hexdigest()

    @cached_property
    def _downloaded_content(self) -> Optional[BytesIO]:
        'Download the file and return its content in a `BytesIO`.'
        try:
            r = get(url=self._url_source, verify=False, timeout=10)
        except Exception as e:
            _logger.error(msg=f'_downloaded_content - caught error: f{e}')
            return None
        if r.status_code != 200:
            _logger.error(
                msg='_downloaded_content - status_code for '
                f'{self._url_source!r} is {r.status_code}')
            return None
        return BytesIO(initial_bytes=r.content) or None

    @cached_property
    def _hash_downloaded(self) -> str:
        'Return the SHA512 hash of the downloaded content.'
        return sha512(self._downloaded_content.getvalue()).hexdigest()

    def _get_extension_with_mimetype(self) -> str:
        """
        Return the enforced extension from the PIL Image, while
        optionally having it converted to another file type.
        """
        im = self._loaded_image
        mime_type = im.get_format_mimetype()
        if mime_type in MIMETYPE_ASSIGNMENTS:
            return MIMETYPE_ASSIGNMENTS[mime_type]['extension'], mime_type
        new_fp = BytesIO()
        if im.mode == 'P' and mime_type != 'image/apng':
            output_image, save_kwargs = \
                create_animated_gif(image=im, size=im.size, do_watermark=False)
            extension = 'gif'
            mime_type = 'image/gif'
        else:
            output_image, save_kwargs = create_animated_webp(
                image=im, size=im.size, do_watermark=False)
            extension = 'webp'
            mime_type = 'image/webp'
        output_image.save(fp=new_fp, **save_kwargs)
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
            _logger.debug(
                msg=f'{self._url_source!r} unidentified, marked as missing.')
            obj_missing = MissingImage.objects.create(
                src=self._url_source[:MISSING_ORIGSRC_LEN])
            raise ImageMissingException(obj_missing)

    def _get_filename_with_mimetype(self) -> Tuple[str, str]:
        """
        Return the filename for this download while converting the the
        downloaded content into one that can be stored and converted
        further later on.
        """
        enforced_extension, mime_type = self._get_extension_with_mimetype()
        url = URL.from_text(text=self._url_source)
        prefix = '.'.join(url.path[-1].split('.')[:-1]) or \
            get_random_safestring(length=5)
        prefix = unidecode(string=prefix)
        for unnecessary_part in self._UNNECESSARY_FILENAME_PARTS:
            prefix = prefix.replace(unnecessary_part, '')
        prefix = self._FILE_SIMPLER_RE.sub('-', prefix).strip('-')
        prefix = prefix[:MAX_FILENAME_SIZE - len(enforced_extension) - 1]
        return '.'.join([prefix, enforced_extension]), mime_type

    def _get_stored_filename(self, abs_dir: Path, filename: str) -> str:
        'Return the final filename part of the fully stored CDN path.'
        while True:
            abspath = abs_dir.joinpath(filename)
            if not abspath.exists():
                break
            if len(filename) >= MAX_FILENAME_SIZE - 9:
                filename = filename[9:]
            filename = '-'.join((get_random_safestring(length=8), filename))
        while True:
            temp_path = abs_dir.joinpath(get_random_safestring())
            if not temp_path.exists():
                break
        temp_path.write_bytes(data=self._downloaded_content.getvalue())
        set_cdn_fileattrs(path=temp_path)
        temp_path.rename(target=abspath)
        _logger.debug(msg=f'Stored {self._url_source!r} into {abspath!r}.')
        return abspath.name

    def _get_cdn_image(self) -> Image:
        'Return a previously or newly created `Image`.'
        # This can modify self._downloaded_content, keep it here!
        filename, mime_type = self._get_filename_with_mimetype()
        cdn_image = Image.objects.filter(
            file_hash=self._hash_downloaded).first()  # type: Image
        if cdn_image:
            _logger.debug(
                msg=f'{self._url_source!r} already downloaded to '
                f'{cdn_image.cdn_path!r}.')
            return cdn_image
        path_parts = (
            'downloaded', *self._timestamp.date().isoformat().split('-'), '')
        abs_dir = get_path_with_ensured_dirs(path_elements=path_parts)
        filename = \
            self._get_stored_filename(abs_dir=abs_dir, filename=filename)
        cdn_metapath = Path(*path_parts[1:-1], filename)
        return Image.objects.create(
            mime_type=mime_type, cdn_path=cdn_metapath,
            file_hash=self._hash_downloaded)

    def _do_preliminary_checks(self):
        'Do preliminary checks, to raise exceptions for early exits.'
        obj_missing = MissingImage.objects.filter(
            src=self._url_source[:MISSING_ORIGSRC_LEN]).first()
        if obj_missing:
            _logger.debug(msg=f'{self._url_source!r} already missing.')
            raise ImageMissingException(obj_missing)
        stored_url = ImageUrl.objects.select_related('image').filter(
            src_hash=self._hash_source).first()  # type: ImageUrl
        if stored_url:
            _logger.debug(
                msg=f'{self._url_source!r} already downloaded to'
                f'{stored_url.image.cdn_path!r}.')
            raise ImageAlreadyDownloadedException(stored_url.image)
        if self._downloaded_content is None or \
                self._hash_downloaded in CANCEL_HASH_SET:
            _logger.debug(msg=f'Added {self._url_source!r} as missing.')
            obj_missing = MissingImage.objects.create(
                src=self._url_source[:MISSING_ORIGSRC_LEN])
            raise ImageMissingException(obj_missing)

    def process(self) -> Optional[Image]:
        'Download and process, return an `Image`, or raise exceptions.'
        self._do_preliminary_checks()
        cdn_image = self._get_cdn_image()
        ImageUrl.objects.create(
            image=cdn_image, orig_src=self._url_source[:MAXLEN_IMAGEURL],
            src_hash=self._hash_source)
        return cdn_image
