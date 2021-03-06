import logging

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.conf import settings
from django.db.models import Model

import magic
import variables
from forum.base.models import Comment, User
from forum.cdn.models import Image, MissingImage
from forum.cdn.utils.downloader import (
    CdnImageDownloader, ImageAlreadyDownloadedError, ImageMissingError)

mime = magic.Magic(mime=True)
logger = logging.getLogger(__name__)

PATH_SIZE_IGNORES = set(['original', 'downloaded', 'xl'])
_HTML = BeautifulSoup(markup='', features='lxml')


def future_assign_model_to_image(cdn_image, model_item):
    if getattr(model_item, 'temp_cdn_image_list', None) is None:
        model_item.temp_cdn_image_list = []
    model_item.temp_cdn_image_list.append(cdn_image)


def wrap_into_picture(img_tag: Tag, cdn_image: Image):
    """
    Use
    https://www.w3schools.com/TAGS/tryit.asp?filename=tryhtml5_picture
    for testing.
    """
    picture_tag = _HTML.new_tag(
        name='picture',
        **{'class': 'embedded-forum-picture', 'data-cdn-pk': cdn_image.pk})
    cdn_metapath = str(cdn_image.cdn_path)
    picture_tag.extend(_HTML.new_tag(
        name='source',
        media=f'(max-width: {settings.CDN["MAXWIDTH"][size]}px)',
        srcset='/'.join((base_url, cdn_metapath)))
        for size, base_url in settings.CDN['URLPREFIX_SIZE'].items()
        if size not in PATH_SIZE_IGNORES)
    original_img = img_tag.replace_with(picture_tag)
    original_img['loading'] = 'lazy'
    # The biggest displayed image is the XL size
    original_img['src'] = '/'.join(
        (settings.CDN['URLPREFIX_SIZE']['xl'], cdn_metapath))
    original_img['width'] = f'{cdn_image.width}px'
    original_img['height'] = f'{cdn_image.height}px'
    picture_tag.append(original_img)


def add_missing_comment_image(
        img_tag: Tag, missing_image: MissingImage, is_newly_missing: bool):
    'Add an image as missing in the content.'
    img_src = img_tag.get('src')
    logger.info(f'Marking object as missing: {img_src!r}')
    img_tag['src'] = settings.IMG_404_PATH
    img_tag['class'] = 'notfound-picture'
    img_tag['data-missing'] = '1'
    img_tag['data-cdn-pk'] = str(missing_image.pk)
    if is_newly_missing:
        variables.MISSING_IMAGE_COUNT += 1
    else:
        variables.ALREADY_MISSING_IMAGE_COUNT += 1


def do_download(img_tag: Tag, model_item: Model):
    used_time = model_item.time if type(model_item) is Comment \
        else model_item.date_joined if type(model_item) is User else None
    img_src = img_tag.get('src')
    processor = CdnImageDownloader(url=img_src, timestamp=used_time)
    try:
        cdn_image = processor.process()
        variables.SUCCESSFULLY_DOWNLOADED += 1
    except ImageMissingError as exc:
        return add_missing_comment_image(
            img_tag=img_tag, missing_image=exc.args[0],
            is_newly_missing=exc.args[1])
    except ImageAlreadyDownloadedError as exc:
        variables.ALREADY_DOWNLOADED_IMAGE_COUNT += 1
        cdn_image = exc.args[0]
    future_assign_model_to_image(cdn_image=cdn_image, model_item=model_item)
    wrap_into_picture(img_tag=img_tag, cdn_image=cdn_image)
