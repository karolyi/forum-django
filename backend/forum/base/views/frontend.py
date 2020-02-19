from typing import Optional, Tuple, Union

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.http.response import \
    HttpResponseRedirect as DjangoHttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic.base import TemplateView

from ..choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from ..exceptions import HttpResponsePermanentRedirect
from ..models import COMMENTS_QS, Comment, Topic
from ..utils.home import collect_topic_page
from ..utils.topic import (
    list_comments, prev_comments_down, replies_up, topic_comment_sanitize)


class TopicListView(TemplateView):
    'Main entry page, with the topic listings.'

    template_name = 'default/base/topic-listing.html'

    def get_context_data(self) -> dict:
        'Fill the context fit topic data.'
        context = super().get_context_data()
        context.update(
            topics_highlighted=collect_topic_page(
                request=self.request,
                topic_type=TOPIC_TYPE_HIGHLIGHTED, page_id=1),
            topics_normal=collect_topic_page(
                request=self.request, topic_type=TOPIC_TYPE_NORMAL, page_id=1),
            topics_archived=collect_topic_page(
                request=self.request,
                topic_type=TOPIC_TYPE_ARCHIVED, page_id=1))
        return context


class TopicCommentListingView(TemplateView):
    'List comments in a certain topic.'

    template_name = 'default/base/topic-comment-listing.html'

    def get_context_data(
            self, topic_slug: str, comment_id: Optional[int] = None) -> dict:
        'Fill the context fit topic data.'
        context = super().get_context_data()
        model_topic, page_comments = list_comments(
            request=self.request, topic_slug=topic_slug,
            comment_id=comment_id)
        context.update(
            page_comments=page_comments, model_topic=model_topic,
            comment_id=comment_id)
        return context

    def get(
            self, request: WSGIRequest, topic_slug: str,
            comment_id: Optional[int] = None) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_id=comment_id)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandRepliesUpRecursive(TemplateView):
    'Expand replies in a topic from a starting comment upwards.'

    def _collect_expanded_comments(
        self, topic_slug: str, comment_id: int, scroll_to_id: int
    ) -> Tuple[Topic, QuerySet]:
        'Collect and return expanded comments.'
        model_comment, search_kwargs_comment = topic_comment_sanitize(
            request=self.request, comment_id=comment_id)
        if model_comment.topic.slug != topic_slug:
            raise HttpResponsePermanentRedirect(url=reverse(
                viewname='forum:base:comments-up-recursive', kwargs=dict(
                    topic_slug=model_comment.topic.slug,
                    comment_id=model_comment.id, scroll_to_id=scroll_to_id)))
        comment_ids = set([model_comment.id])
        iteration_ids = set([model_comment.id])
        while True:
            search_kwargs_comment['prev_comment__in'] = iteration_ids
            qs_comments = Comment.objects.filter(
                **search_kwargs_comment).only('id').order_by()
            iteration_ids = set(x.id for x in qs_comments)
            if len(iteration_ids) == 0:
                # No more comments fetchable
                break
            comment_ids.update(iteration_ids)
        qs_comments = COMMENTS_QS.filter(id__in=comment_ids)
        return model_comment.topic, qs_comments

    def get_context_data(
            self, topic_slug: str, comment_id: int, scroll_to_id: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        model_topic, qs_comments = self._collect_expanded_comments(
            topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        context.update(
            comment_id=comment_id, scroll_to_id=scroll_to_id,
            listing_mode='expandCommentsUpRecursive', model_topic=model_topic,
            qs_comments=qs_comments)
        return context

    def get(
            self, request: WSGIRequest, topic_slug: str,
            comment_id: int, scroll_to_id: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_id=comment_id,
                scroll_to_id=scroll_to_id)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandCommentsUpView(TemplateView):
    """
    Expand replies to a given comment in a non-recursive way. That is,
    only expand the replies to the passed comment ID.
    """
    template_name = 'default/base/comments-expansion.html'

    def get_context_data(
            self, topic_slug: str, comment_id: int, scroll_to_id: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        model_topic, qs_comments = replies_up(
            request=self.request, topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        context.update(
            model_topic=model_topic, comment_id=comment_id,
            qs_comments=qs_comments, scroll_to_id=scroll_to_id,
            listing_mode='expandCommentsUp')
        return context

    def get(
            self, request: WSGIRequest, topic_slug: str,
            comment_id: int, scroll_to_id: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_id=comment_id,
                scroll_to_id=scroll_to_id)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandCommentsDownView(TemplateView):
    """
    Expand previous replies to a given comment in a recursive way. That
    is, expand all the previous replies until the passed comment ID.
    """
    template_name = 'default/base/comments-expansion.html'

    def get_context_data(
            self, topic_slug: str, comment_id: int, scroll_to_id: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        model_topic, qs_comments = prev_comments_down(
            request=self.request, topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
        context.update(
            model_topic=model_topic, comment_id=comment_id,
            qs_comments=qs_comments, scroll_to_id=scroll_to_id,
            listing_mode='expandCommentsDown')
        return context

    def get(
            self, request: WSGIRequest, topic_slug: str,
            comment_id: int, scroll_to_id: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_id=comment_id,
                scroll_to_id=scroll_to_id)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()
