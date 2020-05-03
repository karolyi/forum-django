from pathlib import Path

from django.conf import settings
from django.views.generic.base import RedirectView
from hyperlink import URL

IMG_404_URL = f'{settings.ALLOWED_HOSTS[0]}{settings.IMG_404_PATH}'
RESIZED_PREFIXES = \
    set(x for x in settings.CDN['PATH_SIZES'] if x != 'original')
_PATH_PARAM = settings.IMG_404_PATH.split('/')[1:]


class ResizeImageView(RedirectView):
    'Resizing images to various sizes.'

    def _check_file_exists(self, path_elements: list) -> Path:
        """
        Do sanity checks, return the absolute `Path` of the original
        file, raise `FileNotFoundError` on errors.
        """
        if path_elements[0] not in RESIZED_PREFIXES:
            raise FileNotFoundError
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

    def _get_resized_imageurl(self) -> str:
        'Resize the image if available and return its URL.'
        original_url = self.kwargs['img_path']
        path_elements = original_url.split('/')
        try:
            orig_path = self._check_file_exists(path_elements=path_elements)
        except FileNotFoundError:
            url = URL(
                scheme=self.request.scheme, host=settings.ALLOWED_HOSTS[0],
                path=_PATH_PARAM, port=int(self.request.get_port()))
            return url.to_text()

        print(self.kwargs, original_url, orig_path)
        return '/'

    def get_redirect_url(self, *args, **kwargs) -> str:
        url = self._get_resized_imageurl()
        query_string = self.request.META.get('QUERY_STRING', '')
        if query_string:
            url = f'{url}?{query_string}'
        return url
