from unittest import TestCase

from ..utils import slugify
from django.utils.translation import ugettext_lazy as _


class SlugifyTestCase(TestCase):
    """
    Testing the project's own `slugify` capabilities.
    """

    def test_slugifies_promise(self):
        """
        Should slugify a lazy string.
        """
        self.assertEqual(slugify(_('Name')), 'name')

    def test_slugifies_unicode_data(self):
        """
        Should successfully slugify unicode data.
        """
        self.assertEqual(
            slugify(u'30 \U0001d5c4\U0001d5c6/\U0001d5c1'), '30-kmh')

    def test_disallows_underlines(self):
        """
        Should not allow underlines.
        """
        self.assertEqual(slugify(u'a_b_c'), 'a-b-c')

    def test_disallows_dashes_on_both_ends(self):
        """
        Should not allow dashes at the beginning and at the end.
        """
        self.assertEqual(slugify(u'_a_b_c_'), 'a-b-c')
