import datetime
import logging

from bs4 import BeautifulSoup as bs
from django.apps import apps

import variables
from image_downloader import (
    do_download, future_assign_model_to_image, get_sha512_digest,
    wrap_into_picture)
from markdownparser import parse_to_markdown
from utils import non_naive_datetime_utc
from variables import (
    DEAD_HOSTERS, HTTP_CDN_ROOT, INNER_IMAGE_URLS, NONE_SRC, OLD_SELF_URL,
    comment_uniqid_dict, conn, topic_dict, user_dict)
from video_converter import parse_videos

Comment = apps.get_model('forum_base.Comment')
Image = apps.get_model('forum_cdn.Image')
ImageUrl = apps.get_model('forum_cdn.ImageUrl')
MissingImage = apps.get_model('forum_cdn.MissingImage')

logger = logging.getLogger(__name__)
orig_src_len = ImageUrl._meta.get_field('orig_src').max_length
missing_origsrc_len = MissingImage._meta.get_field('src').max_length


def finish_assign_comment_to_image(comment_item):
    for cdn_image in getattr(comment_item, 'temp_cdn_image_list', []):
        comment_item.images.add(cdn_image)


def select_comment_by_uniqid(topic_id, uniq_id):
    my_cursor = conn.cursor()
    my_cursor.execute((
        'SELECT `commentNumber`, `ownerId`, `unixTime`, '
        '`votingValue`, `hostName`, `prevNumber`, `prevUserId`, '
        '`prevTopicId`, `prevUniqId`, `movedTopicId`, `commentUniqId`, '
        '`commentSource`, `commentParsed`, `edits`, `answersToThis`, '
        f'{topic_id} as `topic_id` FROM `topic_{topic_id}` WHERE '
        '`commentUniqId` = %%s'),
        (uniq_id, ))
    return my_cursor.fetchone()


def build_comment(item):
    if item[10] in comment_uniqid_dict:
        # The comment is already parsed
        return comment_uniqid_dict[item[10]]
    comment_item = Comment(
        number=item[0], user=user_dict[item[1]],
        time=non_naive_datetime_utc(datetime.datetime.fromtimestamp(item[2])),
        voting_value=item[3], host=item[4], ip='0.0.0.0',
        temp_prev_number=item[5], temp_prev_user_id=item[6],
        temp_prev_topic_id=item[7], temp_prev_uniq_id=item[8],
        moved_from=topic_dict[item[9]] if item[9] else None,
        unique_id=item[10], temp_comment_source=item[11],
        content_html=item[12], temp_edits=item[13],
        temp_answerstothis=item[14], topic_id=topic_dict[item[15]].id)
    if item[7] and item[8]:
        if item[8] not in comment_uniqid_dict:
            # Build answered comment, when it's not there yet (recursively)
            old_prev_comment = select_comment_by_uniqid(item[7], item[8])
            comment_item.prev_comment_id = build_comment(old_prev_comment)
        else:
            comment_item.prev_comment_id = comment_uniqid_dict[item[8]]
    parse_content(comment_item)
    comment_item.save()
    finish_assign_comment_to_image(comment_item)
    comment_uniqid_dict[item[10]] = comment_item.id
    return comment_item.id


def fix_if_link(img_tag):
    if img_tag.find_parent().name == 'a' \
            and img_tag.get('name') == 'forumPicture':
        img_tag['class'] = 'embedded-forum-picture'
        del(img_tag['name'])
        parent_tag = img_tag.find_parent()
        parent_tag.unwrap()


def check_already_missing(img_tag):
    """
    Return True if missing, False if not found in the MissingImage table.
    """

    img_src = img_tag.get('src')
    try:
        MissingImage.objects.get(src=img_src[:missing_origsrc_len])
    except MissingImage.DoesNotExist:
        return False

    img_tag['data-missing'] = '1'
    img_tag['src'] = NONE_SRC
    img_tag['class'] = 'notfound-picture'
    logger.info('Object already missing: %s', img_src)
    variables.ALREADY_MISSING_IMAGE_COUNT += 1
    return True


def check_already_downloaded(img_tag, comment_item, content):
    """
    Returns True if already downloaded, False if not.
    """
    orig_src = img_tag.get('src')
    src_hash = get_sha512_digest(orig_src)
    try:
        image_url = ImageUrl.objects.get(src_hash=src_hash)
    except ImageUrl.DoesNotExist:
        return False

    cdn_image = image_url.image
    future_assign_model_to_image(cdn_image, comment_item)
    cdn_url = '/'.join((HTTP_CDN_ROOT, cdn_image.cdn_path))
    logger.info(
        'Object already downloaded: %s, cdn_url: %s', orig_src, cdn_url)
    img_tag['data-cdn-pk'] = cdn_image.pk
    img_tag['src'] = '/'.join((HTTP_CDN_ROOT, cdn_image.cdn_path))
    wrap_into_picture(img_tag, cdn_image.cdn_path, content)
    variables.ALREADY_DOWNLOADED_IMAGE_COUNT += 1
    return True


def download_and_replace(img_tag, comment_item, content):
    img_src = img_tag.get('src')
    if not img_src.startswith('http://') and \
            not img_src.startswith('https://'):
        img_src = 'https://%s' % img_src
        img_tag['src'] = img_src
    logger.info('------- * SEPARATOR * -------')
    if check_already_missing(img_tag):
        return
    if check_already_downloaded(img_tag, comment_item, content):
        return
    do_download(img_tag, comment_item, content)


def fix_comment_image(img_tag, comment_item, content):
    fix_if_link(img_tag)
    if img_tag.get('border'):
        del(img_tag['border'])
    if img_tag.get('align'):
        del(img_tag['align'])
    img_src = img_tag.get('src')
    if img_src is None or img_src.startswith('data:') or \
            img_src.startswith(DEAD_HOSTERS):
        img_tag['src'] = NONE_SRC
        img_tag['class'] = 'notfound-picture'
    if img_src.startswith(('skins/', 'images/')):
        img_src = '/' + img_src
        img_tag['src'] = img_src
    if img_src.startswith(('/images/', '/skins/')):
        img_src = '/static%s' % img_src
        img_tag['src'] = img_src
    if img_src.startswith(OLD_SELF_URL):
        img_src = img_src[len(OLD_SELF_URL):]
        img_tag['src'] = '/static%s' % img_src
        return
    if not img_src.startswith(INNER_IMAGE_URLS):
        download_and_replace(img_tag, comment_item, content)


def parse_content(comment_item):
    content = bs(
        markup='<html><body>%s</body></html>' % comment_item.content_html,
        features='lxml')

    for img_tag in content.select('img'):
        fix_comment_image(img_tag, comment_item, content)
    parse_videos(content)
    comment_item.content_html = content.body\
        .encode_contents()\
        .decode('utf-8')\
        .replace('></source>', '/>')\
        .replace('\r\n', '\n')

    parse_to_markdown(content, comment_item, 'content_md')
