from typing import Dict, Tuple

from django.http.response import Http404
from django.views.generic.base import TemplateView

from ..models import Comment


class CommentListViewBase(TemplateView):
    'Base for comment listing views, with utility functions.'
    _referred_comment: Comment = None

    def _sanitize_comment(self, pk: int) -> Tuple[Comment, Dict]:
        """
        Sanitize the request parameters and check if a requested topic
        is available to the requesting user.

        Raise Http404 if not.

        Return the the extra `kwargs` for the comment selection query
        (don't display comments that are in a topic not visible to the
        user). If this succeeds, will set `self._referred_comment`, with
        only its PK and `topic.slug` set.
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
        return dict(topic_id=self._referred_comment.topic_id)
