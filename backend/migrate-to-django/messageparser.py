import logging

from bs4 import BeautifulSoup as bs
from datetime import datetime

from django.apps import apps
from django.utils.crypto import get_random_string

from markdownparser import parse_to_markdown
from utils import non_naive_datetime_utc, non_naive_datetime_bp
from commentparser import fix_comment_image
from variables import conn, user_dict, message_dict
from video_converter import parse_videos

Mail = apps.get_model('forum_messaging', 'Mail')
GlobalMessage = apps.get_model('forum_messaging', 'GlobalMessage')

logger = logging.getLogger(__name__)
thread_dict = {}


def assign_thread_id(party1, party2):
    thread_id = thread_dict.get(
        '%s-%s' % (party1, party2)) or thread_dict.get(
        '%s-%s' % (party2, party1))
    if thread_id is not None:
        return thread_id
    while True:
        thread_id = get_random_string(length=10)
        if not Mail.objects.filter(thread_id=thread_id).exists():
            break
    thread_dict['%s-%s' % (party1, party2)] = thread_id
    return thread_id


def finish_assign_mail_to_image(model_mail):
    for cdn_image in getattr(
            model_mail, 'temp_cdn_image_list', []):
        model_mail.images.add(cdn_image)


def finish_assign_global_message_to_image(model_global_message):
    for cdn_image in getattr(
            model_global_message, 'temp_cdn_image_list', []):
        model_global_message.images.add(cdn_image)


def parse_content_mail(model_mail):
    # Parse HTML content
    content = bs(
        '<html><body>%s</body></html>' % model_mail.content_html, 'lxml')
    for img_tag in content.select('img'):
        fix_comment_image(img_tag, model_mail, content)
    parse_videos(content)
    # Manually remove erroneous closing tag
    model_mail.content_html = content.body.encode_contents()\
        .decode('utf-8').replace('></source>', '/>').replace('\r\n', '\n')
    parse_to_markdown(content, model_mail, 'content_md')


def parse_content_globalmessage(model_global_message):
    parse_content_mail(model_global_message)


def parse_messaging():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing mails.')
    print('Parsing mails.')
    cursor_inbox = conn.cursor()
    cursor_outbox = conn.cursor()
    message_count = 0
    cursor_inbox.execute(
        'SELECT `userId`, `messageUniqId`, `unixTime`, `senderUserId`, '
        '`state`, `toDelete`, `parsedText` FROM inbox ORDER BY `unixTime`')
    for item in cursor_inbox:
        message_count += 1
        if message_count % 5000 == 0:
            print('counter:', message_count)
        opened_at = created_at = non_naive_datetime_utc(
            datetime.fromtimestamp(item[2]))
        model_mail = Mail(
            sender=user_dict[item[3]], recipient=user_dict[item[0]],
            opened_at=opened_at, status=item[4],
            is_retained_recipient=item[5] == 0, created_at=created_at,
            content_html=item[6], thread_id=assign_thread_id(
                item[0], item[3]))
        message_dict[item[1]] = model_mail
        parse_content_mail(model_mail)
        model_mail.save()
        finish_assign_mail_to_image(model_mail)
        length = cursor_outbox.execute(
            'SELECT `unixTime`, `toDelete` FROM outbox WHERE '
            'messageUniqId = %s', (item[1],))
        if length == 1:
            out_item = cursor_outbox.fetchone()
            model_mail.is_retained_sender = out_item[1] == 0
            opened_at = non_naive_datetime_utc(
                datetime.fromtimestamp(out_item[0]))
        model_mail.save()
        Mail.objects.filter(id=model_mail.id).update(
            created_at=created_at, opened_at=opened_at)

    cursor_outbox.execute(
        'SELECT `userId`, `messageUniqId`, `unixTime`, `sentToUserId`, '
        '`state`, `toDelete`, `parsedText` FROM `outbox` ORDER BY '
        '`messageUniqId`')
    extra_len = 0
    for item in cursor_outbox:
        if item[1] in message_dict:
            continue
        message_count += 1
        if message_count % 5000 == 0:
            print('counter:', message_count)
        extra_len += 1
        opened_at = created_at = non_naive_datetime_utc(
            datetime.fromtimestamp(item[2]))
        model_mail = Mail(
            sender=user_dict[item[0]], recipient=user_dict[item[3]],
            opened_at=opened_at, status=item[4],
            is_retained_sender=item[5] == 0, created_at=created_at,
            content_html=item[6], thread_id=assign_thread_id(
                item[0], item[3]))
        message_dict[item[1]] = model_mail
        parse_content_mail(model_mail)
        model_mail.save()
        finish_assign_mail_to_image(model_mail)
        Mail.objects.filter(id=model_mail.id).update(
            created_at=created_at, opened_at=opened_at)

    print('Parsed mails. Message count: %s, Extra outbox items: %s' % (
        message_count, extra_len))


def parse_global_messages():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing global messages.')
    print('Parsing global messages.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `messageId`, `userId`, `dateTime`, `active`, `subject`, '
        '`messageTextParsed` FROM `globalMessages` ORDER BY `messageId`')
    for item in cursor:
        created_at = non_naive_datetime_bp(item[2])
        model_user = user_dict.get(item[1], user_dict[1])
        model_global_message = GlobalMessage(
            id=item[0], user=model_user, created_at=created_at,
            is_enabled=item[3] == 1, subject=item[4], content_html=item[5])
        parse_content_globalmessage(model_global_message)
        model_global_message.save()
        finish_assign_global_message_to_image(model_global_message)
        GlobalMessage.objects.filter(id=model_global_message.id).update(
            created_at=created_at)

    print('Parsed %s global messages.' % count)
    thread_dict.clear()
    message_dict.clear()
