from unittest import TestCase

from ..exceptions import NotProduceable
from ..utils import cast_to_set_of_int


class CastToSetOfIntTestCase(TestCase):
    """
    Testing `cast_to_set_of_int`.
    """

    def test_returns_set_with_many_elements(self):
        """
        Should return a set when used properly.
        """
        result = cast_to_set_of_int('1-2-3')
        self.assertSetEqual(result, {1, 2, 3})

    def test_raises_notproduceable_when_passed_none(self):
        """
        Should raise `NotProduceable` exception when passed `None`.
        """
        expected_regex = \
            'Invalid input: \'NoneType\' object has no attribute \'split\''
        with self.assertRaisesRegex(
                expected_exception=NotProduceable,
                expected_regex=expected_regex):
            cast_to_set_of_int(None)

    def test_raises_notproduceable_when_passed_garbage(self):
        """
        Should raise `NotProduceable` exception when bumping into
        an error.
        """
        expected_regex = \
            'Invalid input: invalid literal for int\(\) with base 10: \'asd\''
        with self.assertRaisesRegex(
                expected_exception=NotProduceable,
                expected_regex=expected_regex):
            cast_to_set_of_int('asd')

    def test_works_with_alternative_delimiter(self):
        """
        Should work with alternative delimiter.
        """
        result = cast_to_set_of_int('1|2|3', delimiter='|')
        self.assertSetEqual(result, {1, 2, 3})
