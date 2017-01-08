from unittest import TestCase
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http.response import Http404
from django.test import RequestFactory
from forum.base.models import Comment, Topic

from ....utils.topic import list_comments


class ListCommentsTestCase(TestCase):
    """
    Testing `list_comments`.
    """

    User = get_user_model()
    factory = RequestFactory()

    def setUp(self):
        """
        Setting up mocks for the function.
        """
        self.topic = self.page = None
        self.mock_prefetch_for_comments_result = Mock(spec=QuerySet)
        self.patch_get_comments_per_page = patch(
            target='forum.base.utils.topic._get_comments_per_page',
            return_value=50)
        self.patch_get_comment_pageid = patch(
            target='forum.base.utils.topic._get_comment_pageid')
        self.patch_prefetch_for_comments = patch(
            target='forum.base.utils.topic._prefetch_for_comments',
            return_value=self.mock_prefetch_for_comments_result)
        self.patch_comment = patch(
            target='forum.base.utils.topic.Comment', spec=Comment)
        self.patch_topic = patch(
            target='forum.base.utils.topic.Topic', spec=Topic)
        self.patch_paginator = patch(
            target='forum.base.utils.topic.Paginator', spec=Paginator)
        self.mock_get_comment_pageid = self.patch_get_comment_pageid.start()
        self.mock_get_comments_per_page = \
            self.patch_get_comments_per_page.start()
        self.mock_prefetch_for_comments = \
            self.patch_prefetch_for_comments.start()
        self.mock_comment = self.patch_comment.start()
        self.mock_comment.objects.filter.return_value\
            .order_by.return_value = 'comment-filter-return-value'
        self.mock_topic = self.patch_topic.start()
        self.mock_topic.DoesNotExist = Topic.DoesNotExist
        self.mock_topic.objects.get.return_value = 'topic-get-return-value'
        self.mock_comment.DoesNotExist = Comment.DoesNotExist
        self.mock_topic.return_value = 'topic-return-value'
        self.mock_paginator = self.patch_paginator.start()
        self.request = self.factory.get('/foo/')
        self.request.user = AnonymousUser()

    def tearDown(self):
        """
        Finishing mocks.
        """
        self.patch_get_comment_pageid.stop()
        self.patch_get_comments_per_page.stop()
        self.patch_prefetch_for_comments.stop()
        self.patch_comment.stop()
        self.patch_topic.stop()
        self.patch_paginator.stop()

    def assert_normal_flow(self):
        """
        Assert that the execution went through normally after
        prefiltering the topic type.
        """
        self.mock_comment.objects.filter.assert_called_once_with(
            topic='topic-get-return-value')
        self.mock_comment.objects.filter.return_value.order_by\
            .assert_called_once_with('-time')
        self.mock_get_comments_per_page.assert_called_once_with(
            request=self.request)
        self.mock_prefetch_for_comments.assert_called_once_with(
            qs_comments=self.mock_comment.objects.filter.return_value.
            order_by.return_value)
        self.mock_paginator.assert_called_once_with(
            object_list=self.mock_prefetch_for_comments_result, per_page=50)

    def assert_normal_flow_without_commentid(self):
        """
        Assert in this version that `_get_comment_pageid` wasn't called.
        """
        self.assert_normal_flow()
        self.mock_get_comment_pageid.assert_not_called()

    def assert_normal_flow_with_commentid(self, comment_id):
        """
        Assert that `_get_comment_pageid` was called.
        """
        self.assert_normal_flow()
        self.mock_get_comment_pageid.assert_called_once_with(
            qs_comments='comment-filter-return-value', comment_id=comment_id,
            comments_per_page=self.mock_get_comments_per_page.return_value)

    def assert_commentid_passed_and_successful_execution(self, topic, page):
        """
        In here we have a successful execution of the lookup code and
        we get a topic and page returned.
        """
        self.assert_normal_flow_with_commentid(comment_id=123)
        self.mock_paginator.return_value.page.assert_called_once_with(
            number=self.mock_get_comment_pageid.return_value)
        self.assertIs(topic, self.mock_topic.objects.get.return_value)
        self.assertIs(page, self.mock_paginator.return_value.page.return_value)

    def test_raises_http404_if_topic_nonexistent(self):
        """
        Should raise `Http404` when the requested topic does not exist.
        """
        self.mock_topic.objects.get.side_effect = Topic.DoesNotExist()
        with self.assertRaises(expected_exception=Http404):
            list_comments(request=self.request, topic_slug='foo')
        self.mock_topic.objects.get.assert_called_once_with(
            slug='foo', is_staff_only=False, is_enabled=True)

    def test_raises_http404_if_comment_nonexistent(self):
        """
        Should raise `Http404` when the requested comment does not exist.
        """
        self.mock_prefetch_for_comments.exists.return_value = False
        self.mock_prefetch_for_comments_result.exists.return_value = False
        with self.assertRaises(expected_exception=Http404):
            list_comments(request=self.request, topic_slug='foo')
        self.mock_topic.objects.get.assert_called_once_with(
            slug='foo', is_staff_only=False, is_enabled=True)
        self.mock_comment.objects.filter.assert_called_once_with(
            topic='topic-get-return-value')
        self.mock_comment.objects.filter.return_value.order_by\
            .assert_called_once_with('-time')
        self.mock_get_comments_per_page.assert_called_once_with(
            request=self.request)
        self.mock_get_comment_pageid.assert_not_called()
        self.mock_prefetch_for_comments.assert_called_once_with(
            qs_comments=self.mock_comment.objects.filter.return_value.
            order_by.return_value)
        self.mock_paginator.assert_not_called()

    def test_returns_first_page_when_called_without_commentid(self):
        """
        Should return the first page when comment ID is not passed
        and the topic/comment is found.
        """
        topic, page = \
            list_comments(request=self.request, topic_slug='foo')
        self.mock_topic.objects.get.assert_called_once_with(
            slug='foo', is_staff_only=False, is_enabled=True)
        self.assert_normal_flow_without_commentid()
        self.mock_paginator.return_value.page.assert_called_once_with(number=1)
        self.assertIs(topic, self.mock_topic.objects.get.return_value)
        self.assertIs(page, self.mock_paginator.return_value.page.return_value)

    def test_returns_requested_page_when_called_with_commentid(self):
        """
        Should return a page and topic when the comment/topic exists.
        """
        topic, page = list_comments(
            request=self.request, topic_slug='foo', comment_id=123)
        self.mock_topic.objects.get.assert_called_once_with(
            slug='foo', is_staff_only=False, is_enabled=True)
        self.assert_commentid_passed_and_successful_execution(
            topic=topic, page=page)

    def test_user_is_staff(self):
        """
        Should return a page, filtered for staff
        """
        self.request.user = self.User(is_staff=True, is_superuser=False)
        topic, page = list_comments(
            request=self.request, topic_slug='fooo', comment_id=123)
        self.mock_topic.objects.get.assert_called_once_with(
            slug='fooo', is_enabled=True)
        self.assert_commentid_passed_and_successful_execution(
            topic=topic, page=page)

    def test_user_is_superuser(self):
        """
        Should return a page, filtered for staff
        """
        self.request.user = self.User(is_staff=False, is_superuser=True)
        topic, page = list_comments(
            request=self.request, topic_slug='fooo', comment_id=123)
        self.mock_topic.objects.get.assert_called_once_with(
            slug='fooo', is_enabled=True)
        self.assert_commentid_passed_and_successful_execution(
            topic=topic, page=page)

    def test_user_is_superuser_and_staff(self):
        """
        Should return a page, filtered for staff
        """
        self.request.user = self.User(is_staff=True, is_superuser=True)
        topic, page = list_comments(
            request=self.request, topic_slug='fooo', comment_id=123)
        self.mock_topic.objects.get.assert_called_once_with(
            slug='fooo', is_enabled=True)
        self.assert_commentid_passed_and_successful_execution(
            topic=topic, page=page)
