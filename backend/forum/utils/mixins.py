from django.views.generic.base import ContextMixin, View, TemplateView
from django.http.response import JsonResponse
from django.conf import settings


class JsonResponseMixin(ContextMixin, View):
    """
    A mixin that can be used to render a JSON response.
    """
    status_code = 200

    def render_to_response(
            self, context, status_code=None,
            **response_kwargs) -> JsonResponse:
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        json_dumps_params = {}
        if settings.DEBUG:
            json_dumps_params['indent'] = 2
        return JsonResponse(
            data=self.get_json_data(context=context),
            status=status_code or self.status_code,
            json_dumps_params=json_dumps_params,
            **response_kwargs
        )

    def get_json_data(self, context: dict) -> dict:
        """
        Returns an object that will be serialized as JSON by
        `json.dumps()`.
        """
        return {}

    get = TemplateView.get
