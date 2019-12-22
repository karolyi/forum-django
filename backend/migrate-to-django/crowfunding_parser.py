import logging
from datetime import datetime, timedelta

from bs4 import BeautifulSoup as bs
from commentparser import fix_comment_image
from django.apps import apps
from markdownparser import parse_to_markdown
from utils import non_naive_datetime_bp, non_naive_datetime_utc
from variables import conn, topic_dict, user_dict
from video_converter import parse_videos

Project = apps.get_model('forum_crowdfunding', 'Project')
ProjectBacker = apps.get_model('forum_crowdfunding', 'ProjectBacker')

logger = logging.getLogger(__name__)

project_dict = {}
backer_dict = {}


def finish_assign_project_to_image(model_project):
    for cdn_image in getattr(
            model_project, 'temp_cdn_image_list', []):
        model_project.images.add(cdn_image)


def finish_assign_projectbacker_to_image(model_projectbacker):
    for cdn_image in getattr(
            model_projectbacker, 'temp_cdn_image_list', []):
        model_projectbacker.images.add(cdn_image)


def parse_content_html_project(model_project):
    # Parse HTML content
    content = bs(
        '<html><body>%s</body></html>' % model_project.content_html, 'lxml')
    for img_tag in content.select('img'):
        fix_comment_image(img_tag, model_project, content)
    parse_videos(content)
    # Manually remove erroneous closing tag
    model_project.content_html = content.body.encode_contents()\
        .decode('utf-8').replace('></source>', '/>').replace('\r\n', '\n')
    parse_to_markdown(content, model_project, 'content_md')


def parse_content_html_backer(model_projectbacker):
    parse_content_html_project(model_projectbacker)


def parse_crowdfunding_project():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing crowdfunding projects.')
    print('Parsing crowdfunding projects.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `projectId`, `projectName`, `lastUpdatedUnixTime`, '
        '`autoCloseDate`, `ownerId`, `topicId`, `state`, `descriptionParsed` '
        'FROM `projectNames` ORDER BY `projectId`')
    for item in cursor:
        last_updated_at = non_naive_datetime_utc(
            datetime.fromtimestamp(item[2]))
        related_topic = topic_dict.get(item[5])
        ends_at = non_naive_datetime_bp(datetime.combine(
            item[3] + timedelta(days=1), datetime.min.time()))
        model_project = Project(
            name=item[1], owner=user_dict[item[4]],
            last_updated_at=last_updated_at, related_topic=related_topic,
            ends_at=ends_at, status=item[6], content_html=item[7])
        parse_content_html_project(model_project)
        project_dict[item[0]] = model_project
        model_project.save()
        finish_assign_project_to_image(model_project)
        Project.objects.filter(id=model_project.id).update(
            last_updated_at=last_updated_at)
    print('Parsed %s crowdfunding projects.' % count)


def parse_crowdfunding_backers():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing crowdfunding backers.')
    print('Parsing crowdfunding backers.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `projectId`, `ownerId`, `unixTime`, `parsedText` '
        'FROM `projectParticipants` ORDER BY `projectId`')
    count_multiback = 0
    for item in cursor:
        set_backer = backer_dict.get(item[0])
        if set_backer is None:
            set_backer = set()
            backer_dict[item[0]] = set_backer
        if item[1] in set_backer:
            count_multiback += 1
            continue
        set_backer.add(item[1])
        last_updated_at = non_naive_datetime_utc(
            datetime.fromtimestamp(item[2]))
        model_projectbacker = ProjectBacker(
            project=project_dict[item[0]], user=user_dict[item[1]],
            content_html=item[3])
        parse_content_html_backer(model_projectbacker)
        model_projectbacker.save()
        finish_assign_projectbacker_to_image(model_projectbacker)
        ProjectBacker.objects.filter(id=model_projectbacker.id).update(
            last_updated_at=last_updated_at)
    print(
        'Parsed %s crowdfunding backers, multi-backing (mostly b/o deleted '
        'user): %s' % (count, count_multiback))


def parse_crowdfunding():
    parse_crowdfunding_project()
    parse_crowdfunding_backers()
