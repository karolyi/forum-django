from typing import Dict, Optional, Tuple

from django.conf import settings
from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http.response import Http404, HttpResponse
from django.urls.base import reverse
from django.utils.functional import cached_property
from django.views.generic.base import TemplateView

from forum.utils.wsgi import ForumWSGIRequest, ObjectCache

from ..choices import (
    TOPIC_TYPE_ARCHIVED, TOPIC_TYPE_HIGHLIGHTED, TOPIC_TYPE_NORMAL)
from ..exceptions import HttpResponsePermanentRedirect
from ..models import COMMENTS_QS, Comment, Topic
from ..utils.comment import CommentListViewBase
from ..utils.home import collect_topic_page


class TopicListView(TemplateView):
    'Main entry page, with the topic listings.'

    template_name = 'default/base/topic-listing.html'

    def get_context_data(self) -> dict:
        'Fill the context fit topic data.'
        context = super().get_context_data()
        context.update(
            topics_highlighted=collect_topic_page(
                request=self.request, topic_type=TOPIC_TYPE_HIGHLIGHTED,
                page_id=1),
            topics_normal=collect_topic_page(
                request=self.request, topic_type=TOPIC_TYPE_NORMAL, page_id=1),
            topics_archived=collect_topic_page(
                request=self.request, topic_type=TOPIC_TYPE_ARCHIVED,
                page_id=1))
        return context


class TopicCommentListingView(CommentListViewBase):
    'List comments in a certain topic.'

    _referred_topic_pk: int = None
    template_name = 'default/base/topic-comment-listing.html'

    def _sanitize_comment(self) -> Dict:
        """
        Call the `super()` of this and redirect the browser to the
        `Comment`'s current `Topic` if it has changed meanwhile.
        """
        kwargs_comment = \
            super()._sanitize_comment(pk=self.kwargs['comment_pk'])
        if self._referred_comment.topic.slug != self.kwargs['topic_slug']:
            url = reverse(
                viewname='forum:base:topic-comment-listing', kwargs=dict(
                    topic_slug=self._referred_comment.topic.slug,
                    comment_pk=self._referred_comment.pk))
            raise HttpResponsePermanentRedirect(url=url)
        self._referred_topic_pk = self._referred_comment.topic_id
        return kwargs_comment

    def _check_topic_readable(self) -> dict:
        """
        Check if the requested `Topic` exists and is readable to the
        requesting user, raise `Http404` if not.

        Return the keyword arguments for `Comment` filtering.
        """
        kwargs_topic = dict(slug=self.kwargs['topic_slug'], is_enabled=True)
        if not self.request.user.can_view_staff_topic:
            kwargs_topic['is_staff_only'] = False
        try:
            self._referred_topic_pk = \
                Topic.objects.filter(**kwargs_topic).values('pk')[0]['pk']
            return dict(topic_id=self._referred_topic_pk)
        except IndexError:
            raise Http404

    @cached_property
    def comments_per_page(self):
        'Return the shown topics per page for a user.'
        comments_per_page = self.request.session.get('comments-per-page')
        if comments_per_page is not None:
            return comments_per_page
        self.request.session['comments-per-page'] = \
            settings.PAGINATOR_MAX_COMMENTS_PER_PAGE
        return settings.PAGINATOR_MAX_COMMENTS_PER_PAGE

    def _set_pageid(self, qs_comments: QuerySet):
        """
        Set a page number for a given comment ID, so that we can display
        it on the right page.

        Raise `Http404` if the comment doesn't exist.
        """
        comment_pk = self.kwargs.get('comment_pk')
        if not comment_pk:
            try:
                self._page_id = int(self.request.GET.get('page'))
            except (TypeError, ValueError):
                self._page_id = 1
            return
        amount_newer = \
            qs_comments.filter(time__gt=self._referred_comment.time).count()
        self._page_id = amount_newer // self.comments_per_page + 1

    def _list_comments(self) -> Page:
        """
        List a topic page with comments.

        Return the topic model and the requested page containing the
        `comment_id`.
        """
        comment_pk = self.kwargs.get('comment_pk')
        kwargs_comment = self._sanitize_comment() \
            if comment_pk else self._check_topic_readable()
        qs_comments = COMMENTS_QS.with_cache(
            request=self.request).filter(**kwargs_comment)
        self._set_pageid(qs_comments=qs_comments)
        paginator = Paginator(
            object_list=qs_comments, per_page=self.comments_per_page)
        try:
            return paginator.page(number=self._page_id)
        except EmptyPage:
            raise Http404

    def get_context_data(
            self, topic_slug: str, comment_pk: Optional[int] = None) -> dict:
        'Fill the context with the topic data.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_pk=comment_pk)
        page_comments = self._list_comments()
        # Load the CommentQuerySet, this fills the caches
        bool(page_comments.object_list)
        cache = self.request.obj_cache  # type: ObjectCache
        topic = cache.topic[self._referred_topic_pk]
        context.update(
            page_comments=page_comments, page_id=self._page_id,
            topic=topic, comment_pk=comment_pk)
        return context

    def get(
            self, request: ForumWSGIRequest, topic_slug: str,
            comment_pk: Optional[int] = None) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_pk=comment_pk)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandRepliesUpRecursive(CommentListViewBase):
    'Expand replies in a topic from a starting comment upwards.'
    template_name = 'default/base/comments-expansion.html'

    def _sanitize_comment(self):
        """
        Call the `super()` of this and redirect the browser to the
        `Comment`'s current topic if it has changed meanwhile.
        """
        super()._sanitize_comment(pk=self.kwargs['comment_pk'])
        comment = self._referred_comment
        if comment.topic.slug != self.kwargs['topic_slug']:
            raise HttpResponsePermanentRedirect(url=reverse(
                viewname='forum:base:comments-up-recursive', kwargs=dict(
                    topic_slug=comment.topic.slug, comment_pk=comment.pk,
                    scroll_to_pk=self.kwargs['scroll_to_pk'])))

    def _collect_expanded_comments(self) -> Tuple[Topic, QuerySet]:
        'Collect and return expanded comments.'
        self._sanitize_comment()  # set self._referred_comment
        search_kwargs_comment = dict()
        comment_pks = set([self._referred_comment.pk])
        iteration_pks = set([self._referred_comment.pk])
        while True:
            search_kwargs_comment['prev_comment__in'] = iteration_pks
            qs_comments = Comment.objects.order_by().filter(
                **search_kwargs_comment).values_list('pk', flat=True)
            iteration_pks = set(qs_comments)
            if len(iteration_pks) == 0:
                # No more comments fetchable
                break
            comment_pks.update(iteration_pks)
        qs_comments = COMMENTS_QS.filter(
            pk__in=comment_pks).with_cache(request=self.request)
        return self._referred_comment.topic, qs_comments

    def get_context_data(
            self, topic_slug: str, comment_pk: int, scroll_to_pk: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_pk=comment_pk,
            scroll_to_pk=scroll_to_pk)
        topic, qs_comments = self._collect_expanded_comments()
        context.update(
            comment_pk=comment_pk, scroll_to_pk=scroll_to_pk,
            listing_mode='expandCommentsUpRecursive', topic=topic,
            qs_comments=qs_comments)
        return context

    def get(
            self, request: ForumWSGIRequest, topic_slug: str,
            comment_pk: int, scroll_to_pk: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_pk=comment_pk,
                scroll_to_pk=scroll_to_pk)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandCommentsUpView(CommentListViewBase):
    """
    Expand replies to a given comment in a non-recursive way. That is,
    only expand the replies to the passed comment ID.
    """
    template_name = 'default/base/comments-expansion.html'

    def _sanitize_comment(self) -> Dict:
        """
        Call the `super()` of this and redirect the browser to the
        `Comment`'s current topic if it has changed meanwhile.
        """
        search_kwargs_comment = \
            super()._sanitize_comment(pk=self.kwargs['comment_pk'])
        comment = self._referred_comment
        if comment.topic.slug != self.kwargs['topic_slug']:
            url = reverse(
                viewname='forum:base:comments-up', kwargs=dict(
                    topic_slug=comment.topic.slug, comment_pk=comment.pk,
                    scroll_to_pk=self.kwargs['scroll_to_pk']))
            raise HttpResponsePermanentRedirect(url=url)
        return search_kwargs_comment

    def _get_replies_up(self) -> Tuple[Topic, QuerySet]:
        """
        Expand comments in a thread upwards from a given comment ID.

        Return the :model:`forum_base.Topic` and QuerySet of expanded
        comments (time descending)  when successfully gathered them.

        Raise `HttpResponsePermanentRedirect` when the comment exists but
        is in another topic, `Http404` when not found.
        """
        search_kwargs_comment = self._sanitize_comment()
        comment = self._referred_comment
        qs_comments = COMMENTS_QS.filter(
            Q(pk=comment.pk) | Q(prev_comment_id=comment.pk),
            **search_kwargs_comment).with_cache(request=self.request)
        return comment.topic, qs_comments

    def get_context_data(
            self, topic_slug: str, comment_pk: int, scroll_to_pk: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_pk=comment_pk,
            scroll_to_pk=scroll_to_pk)
        topic, qs_comments = self._get_replies_up()
        context.update(
            topic=topic, comment_pk=comment_pk, qs_comments=qs_comments,
            scroll_to_pk=scroll_to_pk, listing_mode='expandCommentsUp')
        return context

    def get(
            self, request: ForumWSGIRequest, topic_slug: str,
            comment_pk: int, scroll_to_pk: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_pk=comment_pk,
                scroll_to_pk=scroll_to_pk)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()


class TopicExpandCommentsDownView(CommentListViewBase):
    """
    Expand previous replies to a given comment in a recursive way. That
    is, expand all the previous replies until the passed comment ID.
    """
    template_name = 'default/base/comments-expansion.html'

    def _sanitize_comment(self) -> Dict:
        """
        Call the `super()` of this and redirect the browser to the
        `Comment`'s current topic if it has changed meanwhile.
        """
        search_kwargs_comment = super()._sanitize_comment(
            pk=self.kwargs['comment_pk'])
        comment = self._referred_comment
        if comment.topic.slug != self.kwargs['topic_slug']:
            url = reverse(
                viewname='forum:base:comments-down', kwargs=dict(
                    topic_slug=comment.topic.slug, comment_pk=comment.pk,
                    scroll_to_pk=self.kwargs['scroll_to_pk']))
            raise HttpResponsePermanentRedirect(url=url)
        return search_kwargs_comment

    def _prev_comments_down(self) -> Tuple[Topic, QuerySet]:
        """
        Expand the previous comments in the thread along with the
        requested comment ID.

        Return the :model:`forum_base.Topic` and QuerySet of expanded
        comments (time descending)  when successfully gathered them.

        Raise `HttpResponsePermanentRedirect` when the comment exists
        but is in another topic, `Http404` when not found.
        """
        # Get the requested comment
        search_kwargs_comment = self._sanitize_comment()
        comment_original = comment = self._referred_comment
        set_comment_pks = set([comment.id])
        while True:
            if comment.prev_comment_id is None:
                # This comment is the root comment, not a previous comment
                break
            search_kwargs_comment['pk'] = comment.prev_comment_id
            try:
                comment = Comment.objects.only(
                    'pk', 'prev_comment_id').get(**search_kwargs_comment)
            except Comment.DoesNotExist:
                # No such comment (or in a topic that's not visible)
                break
            set_comment_pks.add(comment.pk)
        qs_comments = COMMENTS_QS.filter(
            pk__in=set_comment_pks).with_cache(request=self.request)
        return comment_original.topic, qs_comments

    def get_context_data(
            self, topic_slug: str, comment_pk: int, scroll_to_pk: int) -> dict:
        'Add data for the template.'
        context = super().get_context_data(
            topic_slug=topic_slug, comment_pk=comment_pk,
            scroll_to_pk=scroll_to_pk)
        topic, qs_comments = self._prev_comments_down()
        context.update(
            topic=topic, comment_pk=comment_pk, qs_comments=qs_comments,
            scroll_to_pk=scroll_to_pk, listing_mode='expandCommentsDown')
        return context

    def get(
            self, request: ForumWSGIRequest, topic_slug: str,
            comment_pk: int, scroll_to_pk: int) -> HttpResponse:
        'Watch for a redirect exception, redirect when caught.'
        try:
            return super().get(
                request=request, topic_slug=topic_slug, comment_pk=comment_pk,
                scroll_to_pk=scroll_to_pk)
        except HttpResponsePermanentRedirect as exc:
            return exc.get_httpresponse()
            return exc.get_httpresponse()
