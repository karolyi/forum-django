import datetime
import logging

from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from django.conf import settings

from forum.base.models import Comment
from forum.cdn.models import ImageUrl, MissingImage
from image_downloader import do_download
from markdownparser import parse_to_markdown
from utils import non_naive_datetime_ber
from variables import (
    DEAD_HOSTERS, INNER_IMAGE_URLS, OLD_SELF_URL, comment_uniqid_dict, conn,
    topic_dict, user_dict)
from video_converter import parse_videos

logger = logging.getLogger(__name__)
orig_src_len = ImageUrl._meta.get_field('orig_src').max_length
MISSING_ORIGSRC_LEN = MissingImage._meta.get_field('src').max_length


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
        '`commentUniqId` = %s'),
        (uniq_id, ))
    return my_cursor.fetchone()


def build_comment(item):
    if item[10] in comment_uniqid_dict:
        # The comment is already parsed
        return comment_uniqid_dict[item[10]]
    comment_item = Comment(
        number=item[0], user=user_dict[item[1]],
        time=non_naive_datetime_ber(datetime.datetime.fromtimestamp(item[2])),
        voting_value=item[3], host=item[4], ip='0.0.0.0',
        moved_from=topic_dict[item[9]] if item[9] else None,
        unique_id=item[10], content_html=item[12],
        topic_id=topic_dict[item[15]].id)
    comment_item.temp_prev_number = item[5]
    comment_item.temp_prev_user_id = item[6]
    comment_item.temp_prev_topic_id = item[7]
    comment_item.temp_prev_uniq_id = item[8]
    comment_item.temp_comment_source = item[11]
    comment_item.temp_edits = item[13]
    comment_item.temp_answerstothis = item[14],
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
        # img_tag['class'] = 'embedded-forum-picture'
        del(img_tag['name'])
        parent_tag = img_tag.find_parent()
        parent_tag.unwrap()


def download_and_replace(img_tag: Tag, comment_item: Comment):
    img_src = img_tag.get('src')
    if not img_src.startswith('http://') and \
            not img_src.startswith('https://'):
        img_src = 'https://%s' % img_src
        img_tag['src'] = img_src
    logger.info('------- * SEPARATOR * -------')
    do_download(img_tag=img_tag, model_item=comment_item)


def fix_comment_image(img_tag, comment_item, content):
    fix_if_link(img_tag)
    if img_tag.get('border'):
        del(img_tag['border'])
    if img_tag.get('align'):
        del(img_tag['align'])
    img_src = img_tag.get('src')
    if img_src is None or img_src.startswith('data:') or \
            img_src.startswith(DEAD_HOSTERS):
        img_tag['src'] = settings.IMG_404_PATH
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
        download_and_replace(img_tag=img_tag, comment_item=comment_item)


def parse_links(content: Tag):
    'Parse and fix links in the content.'
    for a_tag in content.select(selector='a'):
        a_tag.attrs['rel'] = 'noreferrer noopener'


def parse_content(comment_item: Comment):
    content = bs(
        markup='<html><body>%s</body></html>' % comment_item.content_html,
        features='lxml')
    for img_tag in content.select(selector='img'):
        fix_comment_image(img_tag, comment_item, content)
    parse_links(content=content)
    parse_videos(html=content)
    comment_item.content_html = content.body\
        .decode_contents()\
        .replace('></source>', '/>')\
        .replace('\r\n', '\n')

    parse_to_markdown(content, comment_item, 'content_md')
