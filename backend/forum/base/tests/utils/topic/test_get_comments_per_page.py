from unittest import TestCase

from django.conf import settings
from django.test.client import RequestFactory

from ....utils.topic import _get_comments_per_page

MAX_COMMENTS = settings.PAGINATOR_MAX_COMMENTS_PER_PAGE


class GetCommentsPerPageTestCase(TestCase):
    """
    Testing `_get_comments_per_page()`.
    """

    def setUp(self):
        """
        Setting up stuff for tests.
        """
        self.factory = RequestFactory()
        self.request = self.factory.get('xxx')
        self.request.session = {}

    def test_returns_session_value(self):
        """
        Should return the `comments_per_page` value when set in the
        session.
        """
        self.request.session['comments-per-page'] = 3
        self.assertEqual(_get_comments_per_page(self.request), 3)

    def test_sets_and_returns_default_value(self):
        """
        Should set and return the default value when not set.
        """
        self.assertEqual(
            _get_comments_per_page(self.request), MAX_COMMENTS)
        self.assertEqual(
            self.request.session['comments-per-page'], MAX_COMMENTS)
