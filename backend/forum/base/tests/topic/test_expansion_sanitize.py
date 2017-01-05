from unittest import TestCase
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404
from django.test import RequestFactory
from forum.base.models import Comment

from ...utils.topic import _expansion_sanitize


class ExpansionSanitizeTestCase(TestCase):
    """
    Testing `_expansion_sanitize`.
    """

    factory = RequestFactory()
    User = get_user_model()

    def setUp(self):
        """
        Patch & mock :model:`forum_base.Comment`.
        """
        self.patch_comment = patch(
            target='forum.base.utils.topic.Comment', spec=Comment)
        self.mock_comment = self.patch_comment.start()

    def tearDown(self):
        """
        Stop the comment patch.
        """
        self.patch_comment.stop()

    def is_queryset_properly_parameterized(self):
        """
        Check if the function has properly put the ORM query together.
        """
        self.mock_comment.objects.select_related.assert_called_once_with(
            'topic')
        self.mock_comment.objects.select_related.return_value\
            .only.assert_called_once_with('id', 'topic__slug')

    def check_filters_out_staff_topic(self, user: User):
        """
        Helper function for testers.
        """
        request = self.factory.get('bla')
        request.user = user
        comment, search_kwargs_comment = _expansion_sanitize(
            request=request, comment_id=123)
        self.assertDictEqual(search_kwargs_comment, {
            'topic__is_staff_only': False})
        self.is_queryset_properly_parameterized()
        self.mock_comment.objects.select_related.return_value\
            .only.return_value.get.assert_called_once_with(
                id=123, topic__is_staff_only=False)

    def check_filters_in_staff_topic(self, user: User):
        """
        Helper function for testers.
        """
        request = self.factory.get('bla')
        request.user = user
        comment, search_kwargs_comment = _expansion_sanitize(
            request=request, comment_id=123)
        self.assertDictEqual(search_kwargs_comment, {})
        self.is_queryset_properly_parameterized()
        self.mock_comment.objects.select_related.return_value\
            .only.return_value.get.assert_called_once_with(
                id=123)

    def test_filters_out_staff_topic_when_non_staff(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_staff=False)
        self.check_filters_out_staff_topic(user=user)

    def test_filters_out_staff_topic_when_non_superuser(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_superuser=False)
        self.check_filters_out_staff_topic(user=user)

    def test_filters_out_staff_topic_when_non_superuser_and_non_staff(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_superuser=False, is_staff=False)
        self.check_filters_out_staff_topic(user=user)

    def test_filters_out_staff_topic_when_anonymous_user(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = AnonymousUser()
        self.check_filters_out_staff_topic(user=user)

    def test_filters_in_staff_topic_when_non_superuser_but_staff(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_superuser=False, is_staff=True)
        self.check_filters_in_staff_topic(user=user)

    def test_filters_in_staff_topic_when_superuser_but_non_staff(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_superuser=True, is_staff=False)
        self.check_filters_in_staff_topic(user=user)

    def test_filters_in_staff_topic_when_superuser_and_non_staff(self):
        """
        Should filter out staff topics when the user is non-staff.
        """
        user = self.User(is_superuser=True, is_staff=True)
        self.check_filters_in_staff_topic(user=user)

    def test_raises_http404_when_comment_nonexistent(self):
        """
        Should raise `DoesNotExist` when the comment does not exist.
        """
        request = self.factory.get('bla')
        request.user = AnonymousUser()
        self.mock_comment.DoesNotExist = Comment.DoesNotExist
        self.mock_comment.objects.select_related.return_value.only\
            .return_value.get.side_effect = Comment.DoesNotExist()
        with self.assertRaises(expected_exception=Http404):
            _expansion_sanitize(request=request, comment_id=234)
