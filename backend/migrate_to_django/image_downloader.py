import hashlib
import logging

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.conf import settings
from django.db.models import Model

import magic
import variables
from forum.base.models import Comment, User
from forum.cdn.utils.downloader import CdnImageDownloader

mime = magic.Magic(mime=True)
logger = logging.getLogger(__name__)

PATH_SIZE_IGNORES = set(['original', 'downloaded'])
_HTML = BeautifulSoup(markup='', features='lxml')


def get_sha512_digest(input_data):
    if type(input_data) is str:
        input_data = bytearray(input_data, 'utf-8')
    return hashlib.sha512(input_data).hexdigest()


def future_assign_model_to_image(cdn_image, model_item):
    if getattr(model_item, 'temp_cdn_image_list', None) is None:
        model_item.temp_cdn_image_list = []
    model_item.temp_cdn_image_list.append(cdn_image)


def wrap_into_picture(img_tag: Tag, cdn_metapath: str):
    """
    Use
    https://www.w3schools.com/TAGS/tryit.asp?filename=tryhtml5_picture
    for testing.
    """
    picture_tag = _HTML.new_tag(
        name='picture', **{'class': 'embedded-forum-picture'})
    original_img = img_tag.replace_with(picture_tag)
    original_img['loading'] = 'lazy'
    picture_tag.extend(_HTML.new_tag(
        name='source',
        media=f'(max-width: {settings.CDN["MAXWIDTH"][size]}px)',
        srcset='/'.join((base_url, cdn_metapath)))
        for size, base_url in settings.CDN['URLPREFIX_SIZE'].items()
        if size not in PATH_SIZE_IGNORES)
    picture_tag.append(original_img)


def do_download(img_tag: Tag, model_item: Model):
    used_time = model_item.time if type(model_item) is Comment \
        else model_item.date_joined if type(model_item) is User else None
    img_src = img_tag.get('src')
    processor = CdnImageDownloader(url=img_src, timestamp=used_time)
    cdn_image = processor.process()
    if not cdn_image:
        return
    future_assign_model_to_image(cdn_image, model_item)
    cdn_metapath = str(cdn_image.cdn_path)
    img_src = '/'.join(
        (settings.CDN['URLPREFIX_SIZE']['original'], cdn_metapath))
    img_tag['src'] = img_src
    img_tag['data-cdn-pk'] = str(cdn_image.pk)
    wrap_into_picture(img_tag=img_tag, cdn_metapath=cdn_metapath)
    variables.SUCCESSFULLY_DOWNLOADED += 1
