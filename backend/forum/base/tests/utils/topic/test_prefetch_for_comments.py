from unittest import TestCase
from unittest.mock import Mock

from django.db.models.query import QuerySet

from ....utils.topic import _prefetch_for_comments


class PrefetchForCommentsTestCase(TestCase):
    """
    Testing for `_prefetch_for_comments_test_case()`.
    """

    def test_calls_related_selects(self):
        """
        Should call `select_related` and `prefetch_related` in order
        to prefetch the appropriate fields to not overload the SQL DB
        later on.
        """
        qs_mock_prefetch = Mock(spec=QuerySet)
        qs_mock_prefetch.prefetch_related.return_value = 'stuff'
        qs_mock_select = Mock(spec=QuerySet)
        qs_mock_select.select_related.return_value = qs_mock_prefetch
        result = _prefetch_for_comments(qs_comments=qs_mock_select)
        qs_mock_select.select_related.assert_called_once_with(
            'topic', 'user', 'prev_comment', 'prev_comment__user',
            'prev_comment__topic')
        qs_mock_prefetch.prefetch_related.assert_called_once_with(
            'reply_set', 'reply_set__user', 'reply_set__topic')
        self.assertEqual(result, 'stuff')
