import datetime
import hashlib
import logging
import os
import random
import re
import string
from urllib.parse import unquote, urlparse

import requests
from django.apps import apps
from django.contrib.auth import get_user_model
from unidecode import unidecode

import magic
import variables
from variables import (
    CANCEL_HASH_TUPLE, CDN_FILES_ROOT, FILE_EXTENSIONS, FILE_EXTENSIONS_KEYS,
    FILENAME_MAXLENGTH, HTTP_CDN_ROOT, HTTP_CDN_ROOT_LG, HTTP_CDN_ROOT_MD,
    HTTP_CDN_ROOT_SM, HTTP_CDN_ROOT_XS, NONE_SRC, UNNECESSARY_FILENAME_PARTS)

mime = magic.Magic(mime=True)
logger = logging.getLogger(__name__)
Image = apps.get_model('forum_cdn.Image')
ImageUrl = apps.get_model('forum_cdn.ImageUrl')
MissingImage = apps.get_model('forum_cdn.MissingImage')
Comment = apps.get_model('forum_base.Comment')
Topic = apps.get_model('forum_base.Topic')
User = get_user_model()

missing_origsrc_len = MissingImage._meta.get_field('src').max_length


def get_sha512_digest(input_data):
    if type(input_data) is str:
        input_data = bytearray(input_data, 'utf-8')
    return hashlib.sha512(input_data).hexdigest()


def future_assign_model_to_image(cdn_image, model_item):
    if getattr(model_item, 'temp_cdn_image_list', None) is None:
        model_item.temp_cdn_image_list = []
    model_item.temp_cdn_image_list.append(cdn_image)


def wrap_into_picture(img_tag, cdn_path, content):
    """
    Bootstrap:
    screen-lg: 1200px
    screen-md: 992px
    screen-sm: 768px
    screen-xs: 480px
    """

    from IPython import embed
    embed()
    picture_tag = img_tag.wrap(content.new_tag(name='picture'))
    source_orig = content.new_tag(
        'source', media='(min-width: 1200px)',
        srcset='/'.join((HTTP_CDN_ROOT, cdn_path)))
    source_lg = content.new_tag(
        'source', media='(min-width: 992px)',
        srcset='/'.join((HTTP_CDN_ROOT_LG, cdn_path)))
    source_md = content.new_tag(
        'source', media='(min-width: 768px)',
        srcset='/'.join((HTTP_CDN_ROOT_MD, cdn_path)))
    source_sm = content.new_tag(
        'source', media='(min-width: 480px)',
        srcset='/'.join((HTTP_CDN_ROOT_SM, cdn_path)))
    source_xs = content.new_tag(
        'source', srcset='/'.join((HTTP_CDN_ROOT_XS, cdn_path)))
    picture_tag.insert(0, source_xs)
    picture_tag.insert(0, source_sm)
    picture_tag.insert(0, source_md)
    picture_tag.insert(0, source_lg)
    picture_tag.insert(0, source_orig)


def get_extension(mime_type):
    for mime_type_config in FILE_EXTENSIONS:
        if mime_type.startswith(mime_type_config):
            return FILE_EXTENSIONS[mime_type_config]
    return 'jpg'


def remove_unnecessary_filename_parts(filename):
    for unnecessary_part in UNNECESSARY_FILENAME_PARTS:
        filename = filename.replace(unnecessary_part, '')
    return filename


def normalize_filename(filename, mime_type):
    filename = unidecode(remove_unnecessary_filename_parts(filename))
    name, extension = os.path.splitext(filename)
    name = re.sub('[^a-zA-Z0-9\.\\-]+', '-', name)
    name = re.sub('(^-|-$)', '', name)
    extension = get_extension(mime_type)
    if len(filename) > FILENAME_MAXLENGTH:
        name = name[:FILENAME_MAXLENGTH - len(extension)]
    filename = os.path.extsep.join((name, extension))
    return filename


def create_cdn_file(filename, mime_type, content_data, model_item):
    filename = normalize_filename(filename, mime_type)
    # Add Y-m-d resolution
    now = datetime.datetime.now()
    dir_path = os.path.join(
        now.strftime('%Y'),
        now.strftime('%m'),
        now.strftime('%d'))
    if isinstance(model_item, Comment):
        dir_path = os.path.join(
            model_item.time.strftime('%Y'),
            model_item.time.strftime('%m'),
            model_item.time.strftime('%d'))
    if isinstance(model_item, User):
        dir_path = os.path.join(
            model_item.date_joined.strftime('%Y'),
            model_item.date_joined.strftime('%m'),
            model_item.date_joined.strftime('%d'))
    while True:
        random_seed = ''.join((generate_random() for i in range(10)))
        filename = random_seed + '-' + filename
        file_path = os.path.join(CDN_FILES_ROOT, dir_path, filename)
        if not os.path.exists(file_path):
            break
    if not os.path.exists(os.path.join(CDN_FILES_ROOT, dir_path)):
        os.makedirs(os.path.join(CDN_FILES_ROOT, dir_path))
    file_descriptor = open(file_path, 'wb')
    file_descriptor.write(content_data)
    file_descriptor.close()
    return os.path.join(dir_path, filename)


def check_hash_existing(img_tag, digest_value, model_item, content):
    if digest_value in CANCEL_HASH_TUPLE:
        add_missing_comment_image(img_tag)
        return True
    try:
        cdn_image = Image.objects.get(file_hash=digest_value)
    except Image.DoesNotExist:
        return False
    existing_cdn_url = '/'.join((HTTP_CDN_ROOT, cdn_image.cdn_path))
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
        image=cdn_image, orig_src=orig_src,
        src_hash=get_sha512_digest(orig_src))
    image_url.save()
    future_assign_model_to_image(cdn_image, model_item)
    return True


def generate_random():
    return random.choice(string.ascii_letters + string.digits)


def get_filename_from_url(url):
    result = urlparse(url)
    last_part = result.path.split('/')[-1:][0]
    last_part = unquote(last_part)
    if last_part == '':
        last_part = ''.join((generate_random() for i in range(10)))
    return last_part


def check_right_mime_type(content_data, accepted_mimetypes=('text/html;',)):
    """
    Return False if mimetype not accepted, true when accepted.
    """
    try:
        mime_type = mime.id_buffer(content_data)
    except:
        return False
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
        content_data, FILE_EXTENSIONS_KEYS)
    if not mime_type:
        logger.error('mime_type is %s', mime_type)
        add_missing_comment_image(img_tag)
        return
    filename = get_filename_from_url(orig_src)
    digest_value = get_sha512_digest(content_data)
    if check_hash_existing(img_tag, digest_value, model_item, content):
        return
    cdn_relative_path = create_cdn_file(
        filename, mime_type, content_data, model_item)
    cdn_image = Image(
        mime_type=mime_type, cdn_path=cdn_relative_path,
        file_hash=digest_value)
    cdn_image.save()
    cdn_image_url = ImageUrl(
        image=cdn_image, orig_src=orig_src,
        src_hash=get_sha512_digest(orig_src))
    cdn_image_url.save()
    future_assign_model_to_image(cdn_image, model_item)
    img_tag['src'] = '/'.join((HTTP_CDN_ROOT, cdn_relative_path))
    img_tag['data-cdn-pk'] = '%s' % cdn_image.pk
    wrap_into_picture(img_tag, cdn_relative_path, content)
    variables.SUCCESSFULLY_DOWNLOADED += 1
    logger.info('Object downloaded and added to cdn: %s, cdn_path: %s',
                orig_src, '/'.join((HTTP_CDN_ROOT, cdn_relative_path)))
