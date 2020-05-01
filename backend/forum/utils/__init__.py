from colour_runner.django_runner import ColourRunnerMixin
from django.test.runner import DiscoverRunner
from django.utils.crypto import get_random_string as _get_random_string
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify as django_slugify
from unidecode import unidecode


def slugify(input_data):
    """
    Powerup version of the original django slugify.
    """
    pass_one = unidecode(force_text(input_data))
    pass_two = django_slugify(value=pass_one.replace('_', '-').strip('-'))
    return mark_safe(pass_two)


class DjangoTestRunner(ColourRunnerMixin, DiscoverRunner):
    """
    Colorized test runner for the project:
    """
    pass


def get_random_safestring(
        length=10, allowed_chars=(
            'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')):
    """
    Generate a random password with the given length and given
    allowed_chars. The default value of allowed_chars does not have "I"
    or "O" or letters and digits that look similar -- just to avoid
    confusion.
    """
    return _get_random_string(length=length, allowed_chars=allowed_chars)
