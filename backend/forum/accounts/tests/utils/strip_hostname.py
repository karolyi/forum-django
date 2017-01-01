from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from ...utils import strip_hostname


class StripHostnameTestCase(TestCase):
    """
    Testing the `strip_hostname` function.
    """

    @patch.object(settings, 'ALLOWED_HOSTS', ['localhost'])
    def test_raises_valueerror(self):
        """
        Should raise `ValueError` when the hostname is not allowed.
        """
        with self.assertRaises(ValueError):
            strip_hostname(referrer='stuff')
