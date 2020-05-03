from pathlib import Path

from django.conf import settings
from django.views.generic.base import RedirectView
from hyperlink._url import URL
from PIL.Image import Image
from PIL.Image import open as image_open

from forum.utils import get_relative_path, slugify
from forum.utils.locking import MAX_FILENAME_SIZE, TempLock

IMG_404_URL = f'{settings.ALLOWED_HOSTS[0]}{settings.IMG_404_PATH}'
RESIZED_PREFIXES = \
    set(x for x in settings.CDN['PATH_SIZES'] if x != 'original')
_404_PATH_PARAM = settings.IMG_404_PATH.split('/')[1:]


class ResizeImageView(RedirectView):
    'Resizing images to various sizes.'

    def _check_target_exists(self, path_elements: list):
        'Raise `FileExistsError` when the target file already exists.'
        size_rootpath = settings.CDN['PATH_SIZES'][path_elements[0]]
        target_path = Path(size_rootpath, *path_elements[1:]).absolute()
        try:
            target_path.relative_to(size_rootpath)
        except ValueError:
            # Outside of size root
            raise FileNotFoundError
        if target_path.exists():
            raise FileExistsError

    def _get_original_path(self, path_elements: list) -> Path:
        """
        Do sanity checks, return the absolute `Path` of the original
        file, raise `FileNotFoundError` when the source file is not
        found (or any security issue), `FileExistsError` when the target
        file already exists.
        """
        if path_elements[0] not in RESIZED_PREFIXES:
            raise FileNotFoundError
        self._check_target_exists(path_elements=path_elements)
        file_path = Path(
            settings.CDN['PATH_SIZES']['original'], *path_elements[1:])
        file_path = file_path.resolve()
        try:
            file_path.relative_to(settings.CDN['PATH_SIZES']['original'])
        except ValueError:
            raise FileNotFoundError
        if not file_path.is_file():
            raise FileNotFoundError
        return file_path

    def _get_thumbnail_path(
            self, path_elements: list, orig_path: Path) -> Path:
        'Create the thumbnail and return its CDN absolute `Path`.'
        image = image_open(fp=orig_path)  # type: Image
        width, height = image.size
        requested_size, *cdn_metapath = path_elements
        max_width = settings.CDN['IMAGESIZE'][requested_size]
        new_absolute_path = Path(
            settings.CDN['PATH_SIZES'][requested_size], *cdn_metapath
        ).absolute()
        new_absolute_path.parent.mkdir(parents=True, exist_ok=True)
        if width <= max_width:
            relative_path = get_relative_path(
                path_from=new_absolute_path, path_to=orig_path)
            new_absolute_path.symlink_to(target=relative_path)
            return new_absolute_path
        new_height = int(max_width / width * height)
        image.thumbnail(size=(max_width, new_height), reducing_gap=3.0)
        image.save(fp=new_absolute_path)
        return new_absolute_path

    def _create_url_from_new_path(self, new_path: Path) -> str:
        'Return an URL from the passed absolute path of the new image.'
        parts = new_path.relative_to(settings.CDN['PATH_ROOT']).parts
        return '/'.join((settings.CDN['URL_PREFIX'], *parts))

    def _get_resized_imageurl(self) -> str:
        'Resize the image if available and return its URL.'
        original_url = self.kwargs['img_path']
        path_elements = original_url.lstrip('/').split('/')
        try:
            orig_path = self._get_original_path(path_elements=path_elements)
        except FileNotFoundError:
            url = URL(
                scheme=self.request.scheme, host=settings.ALLOWED_HOSTS[0],
                path=_404_PATH_PARAM, port=int(self.request.get_port()))
            return url.to_text()
        except FileExistsError:
            return '/'.join((settings.CDN['URL_PREFIX'], *path_elements))
        created_absolute_path = self._get_thumbnail_path(
            path_elements=path_elements, orig_path=orig_path)
        return self._create_url_from_new_path(new_path=created_absolute_path)

    def get_redirect_url(self, **kwargs) -> str:
        'Resize the image and return the redirect URL while locking.'
        lock_name = (
            'imageresizer-' +
            slugify(input_data=kwargs['img_path']))[:MAX_FILENAME_SIZE]
        with TempLock(name=lock_name):
            url = self._get_resized_imageurl()
        query_string = self.request.META.get('QUERY_STRING', '')
        if query_string:
            url = f'{url}?{query_string}'
        return url
