from django.http.response import Http404
from django.views.generic.base import TemplateView

from ..models import Comment


class CommentListViewBase(TemplateView):
    'Base for comment listing views, with utility functions.'
    _referred_comment: Comment = None
    _referred_topic_pk: int = None

    def _sanitize_comment(self, pk: int):
        """
        Sanitize the request parameters and check if a requested topic
        is available to the requesting user.

        Raise Http404 if not.

        Sets `self._referred_comment`.
        """
        kwargs_comment = dict(pk=pk, topic__is_enabled=True)
        if not self.request.user.is_staff and \
                not self.request.user.is_superuser:
            # Filter for only non-staff topics
            kwargs_comment['topic__is_staff_only'] = False
        try:
            self._referred_comment = \
                Comment.objects.select_related('topic').only(
                    'pk', 'time', 'topic__slug').get(
                    **kwargs_comment)  # type: Comment
        except Comment.DoesNotExist:
            raise Http404
