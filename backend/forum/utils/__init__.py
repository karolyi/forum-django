from colour_runner.django_runner import ColourRunnerMixin
from django.test.runner import DiscoverRunner
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify as django_slugify
from unidecode import unidecode


def slugify(input_data):
    """
    Powerup version of the original django slugify.
    """
    pass_one = unidecode(force_text(input_data))
    pass_two = django_slugify(pass_one.replace('_', '-').strip('-'))
    return mark_safe(pass_two)


class DjangoTestRunner(ColourRunnerMixin, DiscoverRunner):
    """
    Colorized test runner for the project:
    """
    pass
