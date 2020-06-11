from functools import lru_cache, wraps
from weakref import ref

from colour_runner.django_runner import ColourRunnerMixin
from django.test.runner import DiscoverRunner
from django.utils.crypto import get_random_string as _get_random_string
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify as django_slugify
from unidecode import unidecode

SLUG_TRANSTABLE = str.maketrans('./_', '---')


def slugify(input_data):
    """
    Powerup version of the original django slugify.
    """
    pass_one = unidecode(force_text(input_data))\
        .translate(SLUG_TRANSTABLE)\
        .strip('-')
    pass_two = django_slugify(value=pass_one)
    return mark_safe(pass_two)


def memoized_method(*lru_args, **lru_kwargs):
    'http://stackoverflow.com/a/33672499/1067833'
    def decorator(func):
        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would be never
            # garbage collected.
            self_weak = ref(self)

            @wraps(func)
            @lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)
            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)
        return wrapped_func
    return decorator


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
