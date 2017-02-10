from unittest import TestCase

from ..exceptions import NotProduceable
from ..utils.common import cast_to_set_of_slug


class CastToSetOfSlugTestCase(TestCase):
    """
    Testing `cast_to_set_of_slug`.
    """

    def test_returns_proper_set(self):
        """
        Should return a set of slugs when used properly.
        """
        result = cast_to_set_of_slug(str_input='xxx-a,xxx-b')
        self.assertSetEqual(result, {'xxx-a', 'xxx-b'})

    def test_raises_notproduceable_when_passed_none(self):
        """
        Should raise `NotProduceable` exception when passed `None`.
        """
        expected_regex = \
            'Invalid input: \'NoneType\' object has no attribute \'split\''
        with self.assertRaisesRegex(
                expected_exception=NotProduceable,
                expected_regex=expected_regex):
            cast_to_set_of_slug(None)

    def test_works_with_alternative_delimiter(self):
        """
        Should work with alternative delimiter.
        """
        result = cast_to_set_of_slug('aaa|bbb|ccc', delimiter='|')
        self.assertSetEqual(result, {'aaa', 'bbb', 'ccc'})
