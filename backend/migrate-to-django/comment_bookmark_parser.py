import logging

from django.apps import apps
from utils import non_naive_datetime_bp
from variables import conn, topic_dict, user_dict

Comment = apps.get_model('forum_base', 'Comment')
CommentBookmark = apps.get_model('forum_base', 'CommentBookmark')

logger = logging.getLogger(__name__)


def parse_bookmarks():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing comment bookmarks.')
    print('Parsing comment bookmarks.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `uidTid`, `commentNumber`, `commentUniqId`, `dateTime` '
        'FROM `bookmarks` ORDER BY `uidTid`')
    count_dup = 0
    notfound_error = 0
    for item in cursor:
        uid, tid = item[0].split('-')
        model_user = user_dict.get(int(uid))
        model_topic = topic_dict.get(int(tid))
        if None in [model_user, model_topic]:
            notfound_error += 1
            continue
        try:
            model_comment = Comment.objects.get(unique_id=item[2])
        except Comment.DoesNotExist:
            notfound_error += 1
            continue
        last_updated_at = non_naive_datetime_bp(item[3])
        model_commentbookmark, is_created = CommentBookmark.objects.\
            update_or_create(
                user=model_user, topic=model_topic, comment=model_comment,
                last_updated_at=last_updated_at)
        if not is_created:
            count_dup += 1
        CommentBookmark.objects.filter(id=model_commentbookmark.id).update(
            last_updated_at=last_updated_at)

    print(
        'Parsed %s comment bookmarks, duplicates %s, not found: %s.' % (
            count, count_dup, notfound_error))
