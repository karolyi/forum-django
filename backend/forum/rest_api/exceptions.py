from django.utils.translation import ugettext_lazy as _

from forum.exceptions import ForumExceptionBase


class ApiExceptionBase(ForumExceptionBase):

    """
    Base class for API related exceptions.
    """

    message = _(
        'An exception happened during the API response building process.')
    status_code = 400


class NotProduceable(ApiExceptionBase):

    """
    Raised when a result is not calculable.
    """
    status_code = 400
    message = _('Response is not produceable given the input data.')

    def __init__(self, *args, **kwargs):
        super(NotProduceable, self).__init__(*args, **kwargs)


class UserDoesNotExist(ApiExceptionBase):
    """
    Raised when a requested user is not available in the DB.
    """
    status_code = 400
    message = _('User with the given data does not exist.')

    def __init__(self, *args, **kwargs):
        super(UserDoesNotExist, self).__init__(*args, **kwargs)
