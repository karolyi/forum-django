from typing import Set

from django.utils.translation import ugettext_lazy as _

from .exceptions import NotProduceable


def cast_to_set_of_int(str_input: str, delimiter: str ='-') -> Set[int]:
    """
    Convert a string with the given delimiters into a `set` of `int`.

    Raise `NotProduceable` if an error occurs during conversion.
    """
    try:
        set_result = set(int(x) for x in str_input.split(delimiter))
    except (ValueError, TypeError, AttributeError) as exc:
        raise NotProduceable(_('Invalid input: {message}').format(
            message=exc.args[0]))
    return set_result


def cast_to_set_of_slug(str_input: str, delimiter: str =',') -> Set[str]:
    """
    Convert a delimited list of slugs to a `set` of slugs.
    """
    try:
        set_result = set(x for x in str_input.split(delimiter))
    except (ValueError, TypeError, AttributeError) as exc:
        raise NotProduceable(_('Invalid input: {message}').format(
            message=exc.args[0]))
    return set_result


def tesy(**kwargs: str):
    z = cast_to_set_of_slug(5)
    print(z / 5)
