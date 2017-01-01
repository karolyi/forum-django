from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from ...utils import strip_hostname


class StripHostnameTestCase(TestCase):
    """
    Testing the `strip_hostname` function.
    """

    @patch.object(settings, 'ALLOWED_HOSTS', ['localhost'])
    def test_raises_valueerror_on_garbage(self):
        """
        Should raise `ValueError` when the hostname is not allowed.
        """
        with self.assertRaises(ValueError):
            strip_hostname(referrer='stuff')

    @patch.object(settings, 'ALLOWED_HOSTS', ['only_enabled_host'])
    def test_raises_valueerror_invalid_host(self):
        """
        Should raise `ValueError` when the hostname is not allowed.
        """
        with self.assertRaises(ValueError):
            strip_hostname(referrer='https://invalid_host/testurl')

    @patch.object(settings, 'ALLOWED_HOSTS', ['testhost'])
    def test_returns_valid_path(self):
        """
        Should return the path & query with an allowed hostname.
        """
        uri = strip_hostname(referrer='http://testhost:123/a/b/c?d=e')
        self.assertEqual(uri, '/a/b/c?d=e')
