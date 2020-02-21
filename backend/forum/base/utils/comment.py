from typing import Dict, Tuple

from django.http.response import Http404
from django.views.generic.base import TemplateView

from ..models import Comment


class CommentListViewBase(TemplateView):
    'Base for comment listing views, with utility functions.'

    def _sanitize_topicname(self, comment_pk: int) -> Tuple[Comment, Dict]:
        """
        Sanitize the request parameters and check if a requested topic
        is available to the requesting user.

        Raise Http404 if not.

        Return the :model:`forum_base.Comment` for further evaluation
        with only `topic.slug`(!) set, and the extra kwargs for the
        comment selection query (don't display comments that are in a
        topic not visible to the user).
        """
        search_kwargs_comment = dict(pk=comment_pk, topic__is_enabled=True)
        if not self.request.user.is_staff and \
                not self.request.user.is_superuser:
            # Filter for only non-staff topics
            search_kwargs_comment['topic__is_staff_only'] = False
        try:
            comment = Comment.objects.only(
                'pk', 'topic__slug').get(**search_kwargs_comment)
        except Comment.DoesNotExist:
            raise Http404
        del search_kwargs_comment['pk']
        return comment, search_kwargs_comment
