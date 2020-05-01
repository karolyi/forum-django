import datetime
import hashlib
import logging
from pathlib import Path
from re import compile as re_compile
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.conf import settings
from unidecode import unidecode

import magic
import variables
from forum.base.models import Comment, User
from forum.cdn.models import Image, ImageUrl, MissingImage
from forum.utils import get_random_safestring
from variables import (
    CANCEL_HASH_TUPLE, CDN_FILES_ROOT, FILE_EXTENSIONS, FILE_EXTENSIONS_KEYSET,
    FILENAME_MAXLENGTH, HTTP_CDN_SIZE_ORIGINAL, HTTP_CDN_SIZEURLS, NONE_SRC,
    UNNECESSARY_FILENAME_PARTS)

mime = magic.Magic(mime=True)
logger = logging.getLogger(__name__)
FILE_SIMPLER_RE = re_compile(r'[^a-zA-Z0-9.\-]+')

missing_origsrc_len = MissingImage._meta.get_field('src').max_length
MAXLEN_IMAGEURL = ImageUrl._meta.get_field('orig_src').max_length


def get_sha512_digest(input_data):
    if type(input_data) is str:
        input_data = bytearray(input_data, 'utf-8')
    return hashlib.sha512(input_data).hexdigest()


def future_assign_model_to_image(cdn_image, model_item):
    if getattr(model_item, 'temp_cdn_image_list', None) is None:
        model_item.temp_cdn_image_list = []
    model_item.temp_cdn_image_list.append(cdn_image)


def wrap_into_picture(img_tag: Tag, cdn_path: str, content: BeautifulSoup):
    """
    Use
    https://www.w3schools.com/TAGS/tryit.asp?filename=tryhtml5_picture
    for testing.
    """
    picture_tag = content.new_tag(
        name='picture', **{'class': 'embedded-forum-picture'})
    original_img = img_tag.replace_with(picture_tag)
    picture_tag.extend(content.new_tag(
        name='source',
        media=f'(max-width: {settings.CDN["IMAGESIZE"][size]}px)',
        srcset='/'.join((base_url, str(cdn_path))))
        for size, base_url in HTTP_CDN_SIZEURLS.items())
    picture_tag.append(original_img)


def get_extension(mime_type) -> str:
    for mime_type_config in FILE_EXTENSIONS:
        if mime_type.startswith(mime_type_config):
            return FILE_EXTENSIONS[mime_type_config]
    return 'jpg'


def remove_unnecessary_filename_parts(filename: Path) -> str:
    changed = original = str(filename)
    for unnecessary_part in UNNECESSARY_FILENAME_PARTS:
        changed = changed.replace(unnecessary_part, '')
    return original if original == changed else changed


def normalize_filename(filename: Path, mime_type: str) -> str:
    filename = Path(unidecode(
        string=remove_unnecessary_filename_parts(filename=filename)))
    name = FILE_SIMPLER_RE.sub('-', filename.stem).strip('-')
    extension = get_extension(mime_type)
    if len(str(filename)) > FILENAME_MAXLENGTH:
        name = name[:FILENAME_MAXLENGTH - len(extension)]
    return '.'.join((name, extension))


def create_cdn_file(
    filename: Path, mime_type: str, content_data: bytes, model_item
) -> Path:
    filename = normalize_filename(filename=filename, mime_type=mime_type)
    # Add Y-m-d resolution
    if isinstance(model_item, Comment):
        used_time = model_item.time
    elif isinstance(model_item, User):
        used_time = model_item.date_joined
    else:
        used_time = datetime.datetime.now()
    relative_path = Path(
        used_time.strftime('%Y'), used_time.strftime('%m'),
        used_time.strftime('%d'))
    this_path = CDN_FILES_ROOT.joinpath(relative_path)
    while True:
        filename = f'{get_random_safestring()}-{filename}'
        absolute_path = this_path.joinpath(filename)
        if not absolute_path.exists():
            break
    this_path.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(data=content_data)
    return relative_path.joinpath(filename)


def check_hash_existing(img_tag, digest_value, model_item, content):
    if digest_value in CANCEL_HASH_TUPLE:
        add_missing_comment_image(img_tag)
        return True
    try:
        cdn_image = Image.objects.get(file_hash=digest_value)
    except Image.DoesNotExist:
        return False
    existing_cdn_url = '/'.join((HTTP_CDN_SIZE_ORIGINAL, cdn_image.cdn_path))
    orig_src = img_tag.get('src')
    logger.info(
        'Object hash exists for url %s, existing_cdn_url: %s,'
        ' digest_value is %s',
        orig_src, existing_cdn_url, digest_value)
    img_tag['data-cdn-pk'] = cdn_image.pk
    img_tag['src'] = existing_cdn_url
    wrap_into_picture(img_tag, cdn_image.cdn_path, content)
    variables.ALREADY_DOWNLOADED_IMAGE_COUNT += 1
    image_url = ImageUrl(
        image=cdn_image, orig_src=orig_src[:MAXLEN_IMAGEURL],
        src_hash=get_sha512_digest(orig_src))
    image_url.save()
    future_assign_model_to_image(cdn_image, model_item)
    return True


def get_filename_from_url(url: str) -> Path:
    result = urlparse(url)
    last_part = result.path.split('/')[-1:][0]
    last_part = unquote(last_part)
    if not last_part:
        last_part = get_random_safestring()
    return Path(last_part)


def check_right_mime_type(content_data, accepted_mimetypes=('text/html;',)):
    """
    Return False if mimetype not accepted, true when accepted.
    """
    mime_type = mime.from_buffer(buf=content_data)
    if mime_type is None:
        return False
    for accepted_mimetype in accepted_mimetypes:
        if mime_type.startswith(accepted_mimetype):
            return mime_type
    logger.info('Mimetype %s not in %s', mime_type, accepted_mimetypes)
    return False


def download_file(url):
    logger.debug('Downloading %s', url)
    try:
        r = requests.get(url=url, verify=False, timeout=10)
    except Exception as e:
        logger.error('download_file - caught error: %s', e)
        return None
    if r.status_code != 200:
        return None
    return r.content


def add_missing_comment_image(img_tag):
    img_src = img_tag.get('src')
    logger.info('Marking object as missing: %s', img_src)
    missing_image = MissingImage(src=img_src[:missing_origsrc_len])
    missing_image.save()
    img_tag['src'] = NONE_SRC
    img_tag['class'] = 'notfound-picture'
    img_tag['data-missing'] = '1'
    img_tag['data-cdn-pk'] = '%s' % missing_image.pk
    variables.MISSING_IMAGE_COUNT += 1


def do_download(img_tag, model_item, content):
    orig_src = img_tag.get('src')
    content_data = download_file(orig_src)
    if not content_data:
        logger.error('content_data empty')
        add_missing_comment_image(img_tag)
        return
    mime_type = check_right_mime_type(
        content_data=content_data, accepted_mimetypes=FILE_EXTENSIONS_KEYSET)
    if not mime_type:
        logger.error('mime_type is %s', mime_type)
        add_missing_comment_image(img_tag)
        return
    filename = get_filename_from_url(orig_src)
    digest_value = get_sha512_digest(input_data=content_data)
    if check_hash_existing(img_tag, digest_value, model_item, content):
        return
    cdn_relative_path = create_cdn_file(
        filename=filename, mime_type=mime_type, content_data=content_data,
        model_item=model_item)
    cdn_image = Image(
        mime_type=mime_type, cdn_path=cdn_relative_path,
        file_hash=digest_value)
    cdn_image.save()
    cdn_image_url = ImageUrl(
        image=cdn_image, orig_src=orig_src[:MAXLEN_IMAGEURL],
        src_hash=get_sha512_digest(orig_src))
    cdn_image_url.save()
    future_assign_model_to_image(cdn_image, model_item)
    img_src = '/'.join((HTTP_CDN_SIZE_ORIGINAL, str(cdn_relative_path)))
    img_tag['src'] = img_src
    img_tag['data-cdn-pk'] = '%s' % cdn_image.pk
    wrap_into_picture(img_tag, cdn_relative_path, content)
    variables.SUCCESSFULLY_DOWNLOADED += 1
    logger.info(
        f'Object downloaded and added to cdn: {orig_src}, cdn_path: {img_src}')
