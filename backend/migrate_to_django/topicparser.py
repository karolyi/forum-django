import logging

from bs4 import BeautifulSoup as bs
from django.conf import settings

from commentparser import download_and_replace, fix_if_link, parse_links
from forum.base.models import Topic
from variables import DEAD_HOSTERS, INNER_IMAGE_URLS, OLD_SELF_URL
from video_converter import parse_videos

logger = logging.getLogger(__name__)


def finish_assign_topic_to_image(topic_item):
    for cdn_image in getattr(
            topic_item, 'temp_cdn_image_list', []):
        topic_item.images.add(cdn_image)


def fix_content_image(img_tag, model_item, content):
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
        return
    if img_src.startswith(('skins/', 'images/')):
        img_src = '/' + img_src
        img_tag['src'] = img_src
    if img_src.startswith(('/images/', '/skins/')):
        img_src = '%s%s' % (OLD_SELF_URL, img_src)
        img_tag['src'] = img_src
    if not img_src.startswith(INNER_IMAGE_URLS):
        download_and_replace(img_tag, model_item, content)


def parse_description(topic_item: Topic):
    content = bs(
        markup='<html><body>%s</body></html>' % topic_item.description,
        features='lxml')
    for img_tag in content.select('img'):
        fix_content_image(img_tag, topic_item, content)
    parse_links(content=content)
    parse_videos(html=content)
    topic_item.description = content.body.decode_contents()\
        .replace('></source>', '/>')
