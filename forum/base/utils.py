import re
from django.utils.text import slugify as django_slugify
from django.utils.safestring import mark_safe

SLUGIFY_REGEX = re.compile('-+')


def slugify(input_data):
    """
    I don't like underlines.
    """
    pass_one = django_slugify(input_data)
    pass_two = SLUGIFY_REGEX.sub('-', pass_one.replace('_', '-'))
    return mark_safe(pass_two)
