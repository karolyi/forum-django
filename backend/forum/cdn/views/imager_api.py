from django.conf import settings
from django.utils.functional import cached_property
from django.views.generic.base import RedirectView
from hyperlink._url import URL
from PIL.Image import Image
from PIL.Image import open as image_open

from forum.utils import slugify
from forum.utils.locking import TempLock
from forum.utils.pathlib import Path

from ..utils.image import convert_image
from ..utils.paths import save_new_image, set_cdn_fileattrs

IMG_404_URL = f'{settings.ALLOWED_HOSTS[0]}{settings.IMG_404_PATH}'
RESIZED_PREFIXES = \
    set(settings.CDN['PATH_SIZES']) - set(['downloaded', 'original'])
_404_PATH_PARAM = settings.IMG_404_PATH.split('/')[1:]
LOCK_PREFIX = 'watermarked-'


class ResizeImageView(RedirectView):
    'Resizing images to various sizes.'

    @cached_property
    def _path_elements(self) -> list:
        'Return the elements in the requested path.'
        original_url = self.kwargs['img_path']
        return original_url.lstrip('/').split('/')

    def _sanity_checks(self):
        'Execute sanity checks, raise exceptions on errors.'
        if self._path_elements[0] not in RESIZED_PREFIXES:
            raise FileNotFoundError
        size_rootpath = settings.CDN['PATH_SIZES'][self._path_elements[0]]
        target_path = Path(size_rootpath, *self._path_elements[1:]).absolute()
        try:
            target_path.relative_to(size_rootpath)
        except ValueError:
            # Outside of size root
            raise FileNotFoundError
        if target_path.is_symlink() or target_path.exists():
            raise FileExistsError

    @cached_property
    def _downloaded_path(self) -> Path:
        """
        Do sanity checks, return the absolute `Path` of the downloaded
        file, raise `FileNotFoundError` when the source file is not
        found (or any security issue).
        """
        downloaded_path = Path(
            settings.CDN['PATH_SIZES']['downloaded'], *self._path_elements[1:]
        ).resolve()
        try:
            downloaded_path.relative_to(
                settings.CDN['PATH_SIZES']['downloaded'])
        except ValueError:
            raise FileNotFoundError
        if not downloaded_path.is_file():
            raise FileNotFoundError
        return downloaded_path

    def _create_resized_image(self, max_width: int):
        'If the image is animated, save an animated thumbnail.'
        width, height = self._image.size
        new_height = max_width / width * height
        new_height = int(new_height + 1 if new_height % 1 else new_height)
        image, save_kwargs, *_ = convert_image(
            image=self._image, size=(max_width, new_height), do_watermark=True)
        save_new_image(
            image=image, new_path=self._new_absolute_path,
            save_kwargs=save_kwargs)

    @cached_property
    def _new_absolute_path(self) -> Path:
        'Return a created recursive CDN path while setting mode/gid.'
        requested_size, *cdn_metapath = self._path_elements
        size_root = Path(settings.CDN['PATH_SIZES'][requested_size])
        return size_root.ensure_parentdirs(
            relative_path=cdn_metapath,
            mode=settings.CDN['POSIXFLAGS']['mode_dir'],
            gid=settings.CDN['POSIXFLAGS']['gid'])

    def _get_watermarked_original_path(self) -> Path:
        """
        Return the created watermarked original `Path`while optionally
        locked.
        """
        requested_size, *cdn_metapath = self._path_elements
        size_root = Path(settings.CDN['PATH_SIZES']['original'])
        original_path = size_root.joinpath(*cdn_metapath)
        if original_path.exists():
            return original_path
        size_root.ensure_parentdirs(
            relative_path=cdn_metapath,
            mode=settings.CDN['POSIXFLAGS']['mode_dir'],
            gid=settings.CDN['POSIXFLAGS']['gid'])
        image, save_kwargs, *_ = convert_image(
            image=self._image, size=self._image.size, do_watermark=True)
        save_new_image(
            image=image, new_path=original_path, save_kwargs=save_kwargs)
        return original_path

    @cached_property
    def _watermarked_original_path(self) -> Path:
        """
        Return (and create) the path of the watermarked original image.
        Optionally lock if necessary.
        """
        requested_size, *cdn_metapath = self._path_elements
        if requested_size == 'original':
            return self._get_watermarked_original_path()
        # Another size was requested originally, locking is necessary
        lock_name = LOCK_PREFIX + slugify(
            input_data='-'.join(('original', *cdn_metapath)))
        with TempLock(name=lock_name):
            return self._get_watermarked_original_path()

    def _get_thumbnail_path(self) -> Path:
        'Create the thumbnail and return its CDN absolute `Path`.'
        requested_size = self._path_elements[0]
        if requested_size == 'original':
            return self._watermarked_original_path
        max_width = settings.CDN['MAXWIDTH'][requested_size]
        if self._image.size[0] <= max_width:
            relative_path = self._new_absolute_path.get_relative(
                to=self._watermarked_original_path)
            self._new_absolute_path.symlink_to(target=relative_path)
            set_cdn_fileattrs(path=self._new_absolute_path)
            return self._new_absolute_path
        self._create_resized_image(max_width=max_width)
        return self._new_absolute_path

    def _create_url_from_new_path(self, new_path: Path) -> str:
        'Return an URL from the passed absolute path of the new image.'
        parts = new_path.relative_to(settings.CDN['PATH_ROOT']).parts
        return '/'.join((settings.CDN['URL_PREFIX'], *parts))

    def _get_resized_imageurl(self) -> str:
        'Resize the image if available and return its URL.'
        try:
            self._sanity_checks()
            self._downloaded_path
        except FileNotFoundError:
            url = URL(
                scheme=self.request.scheme, host=settings.ALLOWED_HOSTS[0],
                path=_404_PATH_PARAM, port=int(self.request.get_port()))
            return url.to_text()
        except FileExistsError:
            return '/'.join((settings.CDN['URL_PREFIX'], *self._path_elements))
        with image_open(fp=self._downloaded_path) as image:
            self._image = image  # type: Image
            created_absolute_path = self._get_thumbnail_path()
            del self._image
        return self._create_url_from_new_path(new_path=created_absolute_path)

    def get_redirect_url(self, **kwargs) -> str:
        'Resize the image and return the redirect URL while locking.'
        lock_name = \
            (LOCK_PREFIX + slugify(input_data='-'.join(self._path_elements)))
        with TempLock(name=lock_name):
            url = self._get_resized_imageurl()
        query_string = self.request.META.get('QUERY_STRING')
        if query_string:
            url = f'{url}?{query_string}'
        return url
