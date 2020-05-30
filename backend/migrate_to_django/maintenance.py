import datetime
import logging
import os

import requests
from bs4 import BeautifulSoup as bs
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password  # NOQA
from django.db import connection as django_connection
from django.db import transaction
from markdown import markdown

import phpserialize
import variables
from commentparser import build_comment
from forum.base.choices import TOPIC_TYPE_CHOICES
from forum.base.models import Topic
from forum.cdn.models import Image
from forum.event.models import Event, EventResponse
from forum.rating.models import CommentVote, UserRating
from markdownparser import parse_to_markdown
from topicparser import (
    finish_assign_topic_to_image, fix_content_image, parse_description)
from utils import non_naive_datetime_ber
from variables import (
    comment_uniqid_dict, conn, event_dict, session_dict, topic_dict, user_dict)
from video_converter import parse_videos

logger = logging.getLogger(__name__)
cursor = conn.cursor()

TRUNCATED_TABLES = [
    'forum_base_comment', 'forum_base_commentbookmark', 'forum_base_edit',
    'forum_base_edit_images', 'forum_base_comment_images',
    'forum_base_introductionmodification',
    'forum_base_introductionmodification_images', 'forum_base_topic',
    'forum_base_topic_images', 'forum_base_user',
    'forum_base_user_friended_users', 'forum_base_user_groups',
    'forum_base_user_ignored_users', 'forum_base_user_images',
    'forum_base_user_user_permissions', 'forum_crowdfunding_project',
    'forum_crowdfunding_project_images', 'forum_crowdfunding_projectbacker',
    'forum_crowdfunding_projectbacker_images', 'forum_event_event',
    'forum_event_event_images', 'forum_event_eventresponse',
    'forum_messaging_globalmessage', 'forum_messaging_globalmessage_images',
    'forum_messaging_mail', 'forum_messaging_mail_images', 'forum_poll_choice',
    'forum_poll_question', 'forum_poll_vote', 'forum_rating_commentvote',
    'forum_rating_userrating',
]


def empty_django_db():
    django_cursor = django_connection.cursor()
    django_cursor.execute('SET foreign_key_checks = 0')
    for table in TRUNCATED_TABLES:
        django_cursor.execute(f'TRUNCATE TABLE `{table}`')
    django_cursor.execute('SET foreign_key_checks = 1')
    django_connection.commit()
    transaction.commit()
    for table in TRUNCATED_TABLES:
        django_cursor.execute(f'ALTER TABLE `{table}` AUTO_INCREMENT = 1')
    django_connection.commit()


def cdn_maintenance():
    root_len = len(str(settings.CDN['PATH_SIZES']['downloaded'])) + 1
    logger.info('===== * SEPARATOR * =====')
    logger.info('CDN-MODEL SYNC')
    file_images_set = set()
    for root, dirs, files in os.walk(settings.CDN['PATH_SIZES']['downloaded']):
        if not files:
            continue
        relative_root = root[root_len:]
        for file in files:
            relative_path = '/'.join((relative_root, file))
            file_images_set.add(relative_path)
    db_images_set = set(Image.objects.values_list('cdn_path', flat=True))
    if file_images_set == db_images_set:
        return
    cdn_no_model_set = file_images_set - db_images_set
    variables.CDN_NO_MODEL = len(cdn_no_model_set)
    for relative_path in cdn_no_model_set:
        absolute_path = \
            settings.CDN['PATH_SIZES']['downloaded'].joinpath(relative_path)
        logger.info('No model for CDN file %s, deleting', relative_path)
        absolute_path.unlink()
    cdn_no_file_set = db_images_set - file_images_set
    model_list = Image.objects.filter(cdn_path__in=cdn_no_file_set).only('pk')
    variables.CDN_NO_FILE = len(cdn_no_file_set)
    if model_list:
        logger.info('No CDN file for model(s): %s', model_list)
        with transaction.atomic():
            model_list.delete()


def finish_assign_user_to_image(user_item):
    for cdn_image in getattr(user_item, 'temp_cdn_image_list', []):
        user_item.images.add(cdn_image)


def finish_assign_event_to_image(event_instance):
    for cdn_image in getattr(event_instance, 'temp_cdn_image_list', []):
        event_instance.images.add(cdn_image)


def parse_settings(user_item, settings):
    new_settings_names = [
        'uses_auto_bookmarks', 'mails_own_topic_comments',
        'mails_replies_topic', 'mails_moderation_topic', 'mails_messages',
        'show_replies_comment', 'show_relations', 'is_banned',
        'separate_bookmarked_topics', 'show_outsiders', 'has_chat_enabled',
        'is_approved', 'expand_archived']
    old_settings_names = [
        'is_admin', 'uses_auto_bookmarks', 'mails_own_topic_comments',
        'mails_replies_topic', 'mails_moderation_topic', 'mails_messages',
        'show_replies_comment', 'show_relations', 'is_banned',
        'separate_bookmarked_topics', 'show_outsiders', 'has_chat_enabled',
        'is_activated', 'is_approved', 'modals_only', 'expand_archived']
    counter = 0
    user_temp_setting_dict = {}
    for setting_name in old_settings_names:
        value = settings[counter] == '1'
        if setting_name in new_settings_names:
            setattr(user_item, setting_name, value)
        else:
            user_temp_setting_dict[setting_name] = value
        counter += 1
    user_item.is_staff = user_temp_setting_dict['is_admin']
    user_item.is_active = user_temp_setting_dict['is_activated']


def parse_introductions(user_item):
    for intr_item in [
            'introduction_html_all', 'introduction_html_reg',
            'introduction_html_friends']:
        content = getattr(user_item, intr_item).replace('\n', '<br>\n')
        content = bs(
            markup='<html><body>%s</body></html>' % content, features='lxml')
        for img_tag in content.select('img'):
            fix_content_image(img_tag, user_item, content)
        parse_videos(content)
        # Manually remove erroneous closing tag
        setattr(
            user_item, intr_item, content.body.decode_contents().replace(
                '></source>', '/>').replace('\r\n', '\n'))
        parse_to_markdown(
            content, user_item, intr_item.replace('_html_', '_md_'))


def create_ignored_users_and_inviters():
    for old_id in user_dict:
        user = user_dict[old_id]
        for key in user.temp_ignored_user_list:
            ignored_id = int(user.temp_ignored_user_list[key])
            if ignored_id in user_dict:
                user.ignored_users.add(user_dict[ignored_id])
            else:
                print('%s: Ignored old user ID does not exist: %s' % (
                    user.username, ignored_id))
        if user.temp_inviter_id and user.temp_inviter_id in user_dict:
            user.invited_by = user_dict[user.temp_inviter_id]
            user.save()


def create_friends():
    print('Processing friended users.')
    cursor.execute(
        'SELECT `userId`, `familiarId` FROM `familiarList` '
        'ORDER BY `userId`')
    for item in cursor:
        model_user = user_dict.get(item[0])
        if model_user is None:
            print('Friending old user ID does not exist: %s' % (item[0]))
            continue
        model_friended_user = user_dict.get(item[1])
        if model_friended_user is None:
            print('%s: Friended old user ID does not exist: %s' % (
                user_dict[item[0]], item[1]))
            continue
        model_user.friended_users.add(model_friended_user)


def load_session_dict():
    cursor.execute('SELECT userId, unixTime FROM forumSession')
    for user_id, unix_time in cursor:
        session_dict[user_id] = unix_time


def _parse_user_reviews():
    logger.info('===== * SEPARATOR * =====')
    print('Parsing user ratings.')
    count = cursor.execute(
        'SELECT `ratingId`, `ratedUserId`, `raterUserId`, `approved`, '
        '`ratingValue`, `ratingTime`, `ratingComment` FROM `forumUserRatings` '
        'ORDER BY `ratingId`')
    count_errors = 0
    for item in cursor:
        rater = user_dict.get(item[2])
        ratee = user_dict.get(item[1])
        if None in [rater, ratee]:
            count_errors += 1
            continue
        created_at = non_naive_datetime_ber(item[5])
        content_md = item[6].replace('\r\n', '\n').replace('\n', '  \n')\
            .replace('  \n  \n', '\n\n')
        content_html = markdown(content_md, output_format='html5')
        model_userrating = UserRating(
            is_enabled=item[3] == 1, rater=rater, ratee=ratee, value=item[4],
            created_at=created_at, content_md=content_md,
            content_html=content_html)
        model_userrating.save()
    print('Parsed %s user ratings.' % count)


def parse_users():
    User = get_user_model()
    load_session_dict()
    cursor.execute(
        'SELECT userId, userName, password FROM user ORDER BY userId')
    usernames_lower = set()
    with transaction.atomic():
        for user_id, user_name, user_password in cursor:
            print(
                f'passwords, id: {user_id} username: {user_name}             ',
                end='\r')
            user_dict[user_id] = User(
                username=user_name,
                # password='')
                password=make_password(password=user_password))
            if user_name.lower() in usernames_lower:
                user_dict[user_id].username = f'{user_name}-1'
            usernames_lower.add(user_name.lower())
            # We need an ID for the settings model
            user_dict[user_id].save()
        user_dict[1].is_superuser = True
        cursor.execute(
            'SELECT `userId`, `regDate`, `settings`, `messageIdRead`, '
            '`votingValue`, `votingCount`, `voteLimit`, `quote`, `email`, '
            '`regId`, `maxPostsPerDay`, `sumComments`, `todayComments`, '
            '`yesterdayComments`, `invitations`, `inviterUserId`, '
            '`inviteSuccess`, `reminders`, `usedSkin`, `ignoredUserIdArray`, '
            '`introduction`, `regIntroduction`, `famIntroduction`, '
            '`picemails` FROM `forumUserExt` ORDER BY `userId`')
        for item in cursor:
            user_item = user_dict.get(item[0])
            if not user_item:
                continue
            settings = item[2]
            user_item.date_joined = non_naive_datetime_ber(item[1])
            user_item.last_global_read = item[3]
            user_item.received_comment_vote_sum = item[4]
            user_item.received_comment_vote_count = item[5]
            user_item.comment_vote_hide_limit = item[6]
            user_item.quote = item[7]
            user_item.email = item[8]
            user_item.reg_id = item[9]
            user_item.max_comments_per_day = item[10]
            user_item.comment_count = item[11]
            # user_item.todays_comment_count = item[12]
            # user_item.yesterdays_comment_count = item[13]
            user_item.invitations_today = item[14]
            user_item.temp_inviter_id = item[15]
            user_item.invitations_success = item[16]
            user_item.pw_reminders_today = item[17]
            user_item.used_skin = item[18]
            user_item.temp_ignored_user_list = phpserialize.loads(
                item[19].encode())
            user_item.introduction_html_all = item[20]
            user_item.introduction_html_reg = item[21]
            user_item.introduction_html_friends = item[22]
            user_item.picture_emails = item[23]
            user_item.last_login = non_naive_datetime_ber(
                datetime.datetime.fromtimestamp(session_dict[item[0]]))
            parse_settings(user_item, settings)
            parse_introductions(user_item)
            print(
                f'id: {item[0]} username: {user_item.username}               ',
                end='\r')
            user_item.save()
            finish_assign_user_to_image(user_item)

        create_ignored_users_and_inviters()
        create_friends()
    transaction.commit()
    _parse_user_reviews()
    # transaction.set_autocommit(True)

# ---------------------------------------------------------


def fix_topiclogo_img(topic: Topic):
    'Fix an `[/]?images/topiclogo` prefix.'
    html = bs(markup=topic.name_html, features='lxml')
    for tagname in ['b', 'font', 'i', 'p']:
        found = html.select(selector=tagname)
        for item in found:
            item.unwrap()
    for tag in html.select(selector='img'):
        if 'border' in tag.attrs:
            del tag['border']
        if tag['src'].startswith('/images/topiclogo'):
            tag['src'] = '/media/' + tag['src'][8:]
        elif tag['src'].startswith('images/topiclogo'):
            tag['src'] = '/media/' + tag['src'][7:]
        tag['class'] = 'topic-logo'
    topic.name_html = html.body.decode_contents()


def parse_topics():
    cursor.execute(
        'SELECT `topicId`, `htmlName`, `pureName`, `commentCount`, `ownerId`, '
        '`disabled`, `adminOnly`, `status`, `votingEnabled`, `replyTo`, '
        '`truncateAt`, `currCommentTime`, `lastCommentNumber`, '
        '`currCommentOwnerId`, `currCommentNumber`, `currCommentUniqId`, '
        '`currParsedCommentText`, `descriptionPlain`, `descriptionParsed` '
        'FROM `topicData` ORDER BY `topicId`')
    with transaction.atomic():
        for item in cursor:
            topic_instance = Topic(
                name_html=item[1], name_text=item[2], comment_count=item[3],
                creator=user_dict[item[4]], is_enabled=item[5] == 0,
                is_staff_only=item[6] == 1,
                type=TOPIC_TYPE_CHOICES[item[7]][0],
                is_voting_enabled=item[8] == 1,
                truncate_at=None if item[10] == 0 else item[10],
                description=item[18])
            topic_dict[item[0]] = topic_instance
            fix_topiclogo_img(topic=topic_instance)
            topic_instance.temp_replyto_id = item[9]
            topic_instance.temp_curr_comment_time = item[11]
            topic_instance.temp_last_comment_number = item[12]
            topic_instance.temp_curr_owner_id = item[13]
            topic_instance.temp_curr_comment_number = item[14]
            topic_instance.temp_curr_comment_uniqid = item[15]
            topic_instance.temp_last_comment_text = item[16]
            topic_instance.temp_description_plain = item[17]
            parse_description(topic_instance)
            topic_instance.save()
            finish_assign_topic_to_image(topic_instance)
        for old_id in topic_dict:
            topic_instance = topic_dict[old_id]
            if topic_instance.temp_replyto_id:
                topic_instance.reply_to = topic_dict[
                    topic_instance.temp_replyto_id]
                print('"%s" is replied to "%s"' % (
                    topic_instance.name_text,
                    topic_dict[topic_instance.temp_replyto_id].name_text))
                topic_instance.save()


def update_last_comments():
    for old_id in topic_dict:
        topic_instance = topic_dict[old_id]
        topic_instance.last_comment_id = comment_uniqid_dict[
            topic_instance.temp_curr_comment_uniqid]
        topic_instance.save()
    print('Updated last comments')

# ---------------------------------------------------------


def parse_events():
    logger.info('===== * SEPARATOR * =====')
    cursor.execute(
        'SELECT `meetId`, `enabled`, `startDate`, `endDate`, `ownerId`, '
        '`topicId`, `meetName`, `meetPlace`, `meetTextPlain`, '
        '`meetTextParsed` FROM `meetDates` ORDER BY `meetId`')
    for item in cursor:
        event_instance = Event(
            is_enabled=item[1] == 1, date_start=item[2], date_end=item[3],
            owner=user_dict[item[4]], topic=topic_dict.get(item[5]),
            name=item[6], place=item[7])
        # Parse HTML content
        content = bs(
            markup='<html><body>%s</body></html>' % item[9], features='lxml')
        for img_tag in content.select('img'):
            fix_content_image(img_tag, event_instance, content)
        parse_videos(content)
        # Manually remove erroneous closing tag
        event_instance.content_html = content.body.decode_contents()\
            .replace('></source>', '/>').replace('\r\n', '\n')
        parse_to_markdown(content, event_instance, 'content_md')

        event_instance.save()
        event_dict[item[0]] = event_instance
        finish_assign_event_to_image(event_instance)
    print('Parsed events.')
    logger.info('Parsed events')


def parse_event_responses():
    logger.info('===== * SEPARATOR * =====')
    cursor.execute(
        'SELECT `meetId`, `userId`, `dateTime` FROM `meetParticipants` '
        'ORDER BY `meetId`, `userId`')
    for item in cursor:
        model_response = EventResponse(
            event=event_dict[item[0]], inviter=None,
            invitee=user_dict[item[1]], status=1,  # 1 as Going
        )
        model_response.save()
        EventResponse.objects.filter(id=model_response.id).update(
            last_modified=non_naive_datetime_ber(item[2]))
    print('Parsed event responses.')
    logger.info('Parsed event responses.')


# ---------------------------------------------------------


def parse_comments():
    counter = 0
    topic_id_list = list(topic_dict.keys())
    topic_id_list.sort()
    for old_topic_id in topic_id_list:
        print('\nDoing %s: "%s"' % (
            old_topic_id, topic_dict[old_topic_id].name_text))
        cursor.execute((
            'SELECT `commentNumber`, `ownerId`, `unixTime`, '
            '`votingValue`, `hostName`, `prevNumber`, `prevUserId`, '
            '`prevTopicId`, `prevUniqId`, `movedTopicId`, `commentUniqId`, '
            '`commentSource`, `commentParsed`, `edits`, `answersToThis`, '
            '%s as `topic_id` FROM `topic_%s` ORDER BY `commentUniqId`') %
            (old_topic_id, old_topic_id))
        counter = 0
        while cursor.rownumber < cursor.rowcount:
            with transaction.atomic():
                for item in cursor.fetchmany(20000):
                    counter += 1
                    build_comment(item)
            print('counter: %s' % counter)
            transaction.commit()


def parse_comment_votes():
    logger.info('------- * SEPARATOR * -------')
    logger.info('Parsing comment votes.')
    print('Parsing comment votes.')
    response = requests.get(
        'https://crxforum.ksol.io/exportCommentVotes.php', timeout=300)
    count_errors = 0
    count_dup = 0
    for count, item in enumerate(response.json()):
        model_user = user_dict.get(item['uid'])
        if model_user is None:
            count_errors += 1
            continue
        comment_id = comment_uniqid_dict.get(item['uniqId'])
        if comment_id is None:
            count_errors += 1
            continue
        model_commentvote, is_created = CommentVote.objects.update_or_create(
            comment_id=comment_id, user=model_user, defaults={
                'value': item['value']
            })
        if not is_created:
            count_dup += 1

    print('Parsed %s comment votes. Not found: %s, Duplicate: %s' % (
        count, count_errors, count_dup))
