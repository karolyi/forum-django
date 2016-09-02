from django.http.response import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _


class ApiExceptionBase(Exception):

    """
    Base class for API related exceptions.
    """

    message = _('An exception happened during the response building process.')
    status_code = 400

    def __init__(self, message=None):
        super(ApiExceptionBase, self).__init__()
        if message is not None:
            self.message = message

    def json_response(self):
        """
        Returning an HTTP error response in JSON format.
        """
        if type(self.message) is not str:
            # Evaluate for lazy strings (translations)
            self.message = str(self.message)

        response = JsonResponse({
            'status': 'error',
            'type': type(self).__name__,  # The instance class name
            'message': self.message
        }, safe=False)
        response.status_code = self.status_code
        return response

    def html_response(self):
        """
        Return a HTTP error and a HTML page.
        """
        if type(self.message) is not str:
            # Evaluate for lazy strings (translations)
            self.message = str(self.message)

        response = HttpResponse(self.message, content_type='text/plain')
        response.status_code = self.status_code
        return response


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
