from unittest import TestCase
from unittest.mock import Mock

from django.db.models.query import QuerySet
from django.http.response import Http404
from forum.base.models import Comment

from ....utils.topic import _get_comment_pageid


class GetCommentPageIdTestCase(TestCase):
    """
    Testing `_get_comment_pageid`.
    """

    mock_comment = Comment(time=555)

    def setUp(self):
        """
        Patching and starting mocks.
        """
        self.mock_qs_comments = Mock(spec=QuerySet)
        self.mock_qs_comments.get.return_value = self.mock_comment
        self.comment_id = 765

    def check_queryset_parameterized_properly(self):
        """
        Check here the parameters with which `mock_qs_comments` was
        called.
        """
        self.mock_qs_comments.get.assert_called_once_with(id=self.comment_id)
        self.mock_qs_comments.filter.assert_called_once_with(time__gt=555)
        self.mock_qs_comments.filter.return_value.count\
            .assert_called_once_with()

    def test_raises_http404_when_comment_nonexistent(self):
        """
        Should raise `Http404` when the requested comment does not exist.
        """
        self.mock_qs_comments.get.side_effect = Comment.DoesNotExist()
        with self.assertRaises(expected_exception=Http404):
            _get_comment_pageid(
                qs_comments=self.mock_qs_comments, comment_id=self.comment_id,
                comments_per_page=4)

    def test_returns_pageid_equals_3(self):
        """
        Should return a page ID for a comment ID that exists.

        When we have 6 newer comments and the displayed number of
        comments per page is 3, then whe should be on the 3rd page.
        """
        # 6 newer comment
        self.mock_qs_comments.filter.return_value.count.return_value = 6
        page_id = _get_comment_pageid(
            qs_comments=self.mock_qs_comments, comment_id=self.comment_id,
            comments_per_page=3)
        self.assertEqual(page_id, 3)
        self.check_queryset_parameterized_properly()

    def test_returns_pageid_equals_3_with_7_newer_comments(self):
        """
        Should return a page ID for a comment ID that exists.

        When we have 7 newer comments and the displayed number of
        comments per page is 3, then whe should be on the 3rd page.
        """
        # 6 newer comment
        self.mock_qs_comments.filter.return_value.count.return_value = 7
        page_id = _get_comment_pageid(
            qs_comments=self.mock_qs_comments, comment_id=self.comment_id,
            comments_per_page=3)
        self.assertEqual(page_id, 3)
        self.check_queryset_parameterized_properly()

    def test_returns_pageid_equals_2_with_6_newer_comments(self):
        """
        Should return a page ID for a comment ID that exists.

        When we have 6 newer comments and the displayed number of
        comments per page is 4, then whe should be on the 3rd page.
        """
        # 6 newer comment
        self.mock_qs_comments.filter.return_value.count.return_value = 6
        page_id = _get_comment_pageid(
            qs_comments=self.mock_qs_comments, comment_id=self.comment_id,
            comments_per_page=4)
        self.assertEqual(page_id, 2)
        self.check_queryset_parameterized_properly()
