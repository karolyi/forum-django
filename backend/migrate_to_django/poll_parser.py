import logging

from django.apps import apps
from utils import non_naive_datetime_ber
from variables import conn, topic_dict, user_dict

Question = apps.get_model('forum_poll', 'Question')
Choice = apps.get_model('forum_poll', 'Choice')
Vote = apps.get_model('forum_poll', 'Vote')

logger = logging.getLogger(__name__)

question_dict = {}
choice_dict = {}


def _parse_poll_questions():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing poll questions.')
    print('Parsing poll questions.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `votingId`, `topicId`, `active`, `dateTime`, `userId`, '
        '`questionText` FROM `votingQuestions` ORDER BY `votingId`')
    for item in cursor:
        created_at = non_naive_datetime_ber(item[3])
        model_question = Question(
            text=item[5], topic=topic_dict.get(item[1]),
            created_by=user_dict[item[4]], created_at=created_at,
            is_enabled=item[2] == 1)
        question_dict[item[0]] = model_question
        model_question.save()
        Question.objects.filter(id=model_question.id).update(
            created_at=created_at)
    print('Parsed %s poll questions.' % count)


def _parse_poll_choices():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing poll choices.')
    print('Parsing poll choices.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `votingId`, `answerId`, `votings`, `answerText` FROM '
        '`votingAnswers` ORDER BY `votingId`, `answerId`')
    for item in cursor:
        model_choice = Choice(
            question=question_dict[item[0]], text=item[3], votes=item[2],
            order=item[1])
        choice_dict['%s-%s' % (item[0], item[1])] = model_choice
        model_choice.save()
    print('Parsed %s poll choices.' % count)


def _parse_poll_votes():
    logger.info('================= *** SEPARATOR *** =================')
    logger.info('Parsing poll votes.')
    print('Parsing poll votes.')
    cursor = conn.cursor()
    count = cursor.execute(
        'SELECT `votingId`, `userId`, `dateTime`, `answerId` FROM '
        '`votedUsers` ORDER BY `votingId`, `answerId`')
    count_dup = 0
    for item in cursor:
        last_modified_at = non_naive_datetime_ber(item[2])
        model_vote, is_created = Vote.objects.update_or_create(
            user=user_dict[item[1]], question=question_dict[item[0]],
            defaults={
                'choice': choice_dict['%s-%s' % (item[0], item[3])],
                'last_modified_at': last_modified_at
            })
        if not is_created:
            count_dup += 1
        Vote.objects.filter(id=model_vote.id).update(
            last_modified_at=last_modified_at)
    print('Parsed %s poll votes, duplicated votes: %s' % (count, count_dup))


def _update_choice_vote_count():
    for model_choice in Choice.objects.all():
        model_choice.votes = model_choice.vote_set.count()
        model_choice.save()


def parse_polls():
    _parse_poll_questions()
    _parse_poll_choices()
    _parse_poll_votes()
    _update_choice_vote_count()
