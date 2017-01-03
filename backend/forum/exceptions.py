from django.http.response import HttpResponse, JsonResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class ForumExceptionBase(Exception):

    """
    Base exception class for the forum.
    """

    message = _('An exception happened during the response building process.')
    status_code = 400

    def __init__(self, message=None):
        super(ForumExceptionBase, self).__init__()
        if message is not None:
            self.message = message

    def json_response(self):
        """
        Returning an HTTP error response in JSON format.
        """
        self.message = force_text(self.message)
        response = JsonResponse({
            'status': 'error',
            'type': type(self).__name__,  # The instance class name
            'message': self.message
        }, safe=False)
        response.status_code = self.status_code
        return response

    def textual_response(self):
        """
        Return a HTTP error and a HTML page.
        """
        self.message = force_text(self.message)
        response = HttpResponse(self.message, content_type='text/plain')
        response.status_code = self.status_code
        return response

    def __str__(self):
        return self.message
