from typing import Optional

from django.utils.functional import cached_property

from ..models import IframelyResponse


class UnparseableResponseError(Exception):
    'Raised when a link is unparseable by iframely.'

    def __init__(self, response: IframelyResponse):
        self.response = response


class LinkParser(object):
    'Provide preview embeds for passed links with iframely.'
    _response: IframelyResponse

    def __init__(self, url: str):
        self._url = url

    @cached_property
    def biggest_thumbnail_url(self) -> Optional[str]:
        links = self._response.loaded_json.get('links', [])
        links = filter(lambda x: 'thumbnail' in x.get('rel', []), links)
        return links

    def process(self) -> str:
        'Return the preview HTML content.'
        self._response = IframelyResponse.objects.get_for_url(url=self._url)
        if self._response.response_code != 200:
            raise UnparseableResponseError(response=self._response)
        self._evaluate_response()
