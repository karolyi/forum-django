from django.utils.text import slugify as django_slugify
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


def slugify(input_data):
    """
    I don't like underlines in URLs.
    """
    pass_one = force_text(input_data)
    pass_two = django_slugify(pass_one.replace('_', '-'))
    return mark_safe(pass_two)
