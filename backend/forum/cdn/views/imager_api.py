from django.views.generic.base import RedirectView


class ResizeImageView(RedirectView):
    'Resizing images to various sizes.'

    def _get_resized_imageurl(self) -> str:
        'Resize the image if available and return its url.'
        original_url = self.kwargs['img_url']
        print(self.kwargs, original_url)
        return '/'

    def get_redirect_url(self, *args, **kwargs) -> str:
        url = self._get_resized_imageurl()
        query_string = self.request.META.get('QUERY_STRING', '')
        if query_string:
            url = f'{url}?{query_string}'
        return url
