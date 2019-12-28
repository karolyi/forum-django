from typing import Optional, Union

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from django.http.response import \
    HttpResponseRedirect as DjangoHttpResponsePermanentRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView

from ..choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from ..exceptions import HttpResponsePermanentRedirect
from ..utils.home import collect_topic_page
from ..utils.topic import (
    list_comments, prev_comments_down, replies_up, replies_up_recursive)


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
                request=self.request,
                topic_type=TOPIC_TYPE_NORMAL, page_id=1),
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
            return exc.get_http_response()


def expand_comments_up_recursive(
        request: WSGIRequest, topic_slug: str, comment_id: int,
        scroll_to_id: int
) -> Union[HttpResponse, DjangoHttpResponsePermanentRedirect]:
    """
    Expand replies to a given comment, by expanding all that is a reply
    to the given comment upwards.
    """
    try:
        model_topic, qs_comments = replies_up_recursive(
            request=request, topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
    except HttpResponsePermanentRedirect as exc:
        return exc.http_response()
    return render(
        request=request, template_name='default/base/comments-expansion.html',
        context={
            'model_topic': model_topic,
            'comment_id': comment_id,
            'qs_comments': qs_comments,
            'scroll_to_id': scroll_to_id,
            'listing_mode': 'expandCommentsUpRecursive'})


def expand_comments_up(
    request: WSGIRequest, topic_slug: str, comment_id: int, scroll_to_id: int
) -> Union[HttpResponse, DjangoHttpResponsePermanentRedirect]:
    """
    Expand replies to a given comment in a non-recursive way. That is,
    only expand the replies to the passed comment ID.
    """
    try:
        model_topic, qs_comments = replies_up(
            request=request, topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
    except HttpResponsePermanentRedirect as exc:
        return exc.http_response()
    return render(
        request=request, template_name='default/base/comments-expansion.html',
        context={
            'model_topic': model_topic,
            'comment_id': comment_id,
            'qs_comments': qs_comments,
            'scroll_to_id': scroll_to_id,
            'listing_mode': 'expandCommentsUp',
        })


def expand_comments_down(
    request: WSGIRequest, topic_slug: str, comment_id: int,
    scroll_to_id: int
) -> Union[HttpResponse, DjangoHttpResponsePermanentRedirect]:
    """
    Expand previous replies to a given comment in a recursive way. That
    is, expand all the previous replies until the passed comment ID.
    """
    try:
        model_topic, qs_comments = prev_comments_down(
            request=request, topic_slug=topic_slug, comment_id=comment_id,
            scroll_to_id=scroll_to_id)
    except HttpResponsePermanentRedirect as exc:
        return exc.http_response()
    return render(
        request=request, template_name='default/base/comments-expansion.html',
        context={
            'model_topic': model_topic,
            'comment_id': comment_id,
            'qs_comments': qs_comments,
            'scroll_to_id': scroll_to_id,
            'listing_mode': 'expandCommentsDown',
        })
