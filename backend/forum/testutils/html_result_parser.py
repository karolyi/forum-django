from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.http.response import HttpResponse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from forum.base.choices import LIST_TOPIC_TYPE


class HtmlResultParserBase(object):
    """
    Tool for parsing the rendered HTML content with end-to-end testing.
    """

    def __init__(self, test: TestCase, response: HttpResponse) -> None:
        """
        Store the passed `TestCase` object into self, for later asserts.
        """
        self.test = test
        self.response = response
        self._assert_statuscode_200()
        self._parse_result()

    def _get_inner_html(self, tag: Tag):
        """
        Return the `innerHTML` of a given passed content list (from a
        `Tag`).
        """
        return ''.join(map(str, tag.contents))

    def _assert_statuscode_200(self) -> None:
        self.test.assertEqual(self.response.status_code, 200)

    def _parse_result(self) -> None:
        """
        Parse the response output to `BeautifulSoup` structure.
        """
        markup = self.response.content.decode('utf-8')
        self.soup = BeautifulSoup(markup=markup, features='lxml')

    def _remove_templates(self) -> None:
        """
        Remove all `<template>` tags since they their content is
        irrelevant at testing time.
        """
        template = self.soup.template
        # Remove ALL the templates!
        while template is not None:
            self.soup.template.decompose()
            template = self.soup.template


class CommentsUpRecursiveParser(HtmlResultParserBase):
    """
    Parsing the result of `comments_up_recursive` view.
    """

    def __init__(self, *args, **kwargs) -> None:
        super(CommentsUpRecursiveParser, self).__init__(*args, **kwargs)
        self.rendered_comments = {}
        self.last_cached_comment = None

    def assert_commentid_contains_content(
            self, comment_id: int, content: str) -> None:
        """
        Assert that a given rendered comment's content contains a given
        passed text snippet.
        """
        comment_wrapper = self.soup.main.article.find(
            name='section', attrs={'data-comment-id': comment_id})
        self.test.assertIsNotNone(comment_wrapper)
        self.rendered_comments[comment_id] = comment_wrapper
        self.last_cached_comment = comment_wrapper
        inner_html = self._get_inner_html(
            tag=self.last_cached_comment.find(
                name='div', class_='comment-content'))
        self.test.assertIn(member=content, container=inner_html)

    def assert_no_more_comments(self) -> None:
        """
        Assert that only the previously looked up comments are rendered
        in the HTML response.
        """
        self._remove_templates()
        rendered_comments = self.soup.main.article.find_all(
            name='section', class_='topic-comment-wrapper')
        id_list = []
        for comment in rendered_comments:
            id_list.append(int(comment['data-comment-id']))
        for comment_id in self.rendered_comments.keys():
            id_list.remove(comment_id)
        if id_list:
            self.test.fail(msg=_(
                'There are more comments with IDs {ids}').format(
                ids=', '.join(map(str, id_list))))


class TopicListingParser(HtmlResultParserBase):
    """
    A test result parser for the `topic_listing` view.
    """

    def __init__(self, *args, **kwargs) -> None:
        super(TopicListingParser, self).__init__(*args, **kwargs)

    def parse_as_full_page(self):
        """
        Parse the HTML as a full page.
        """
        self.listed_topic_categories = LIST_TOPIC_TYPE
        self.listed_topics = {
            topic_type: [] for topic_type in LIST_TOPIC_TYPE}
        for topic_type in LIST_TOPIC_TYPE:
            self.listed_topics[topic_type] = \
                self.soup.main.find(
                    name='div',
                    class_='topic-type-{topic_type}'.format(
                        topic_type=topic_type)).find_all(
                    name='div', class_='topic-list-item-row')
        self.asserted_topic_slugs = {
            topic_type: set() for topic_type in LIST_TOPIC_TYPE}

    def parse_as_one_topic_page(self, topic_type: str) -> None:
        """
        Parse the resulted HTML as it's only one served page of a
        topic list, served through the api on page change.
        """
        self.listed_topic_categories = [topic_type]
        self.listed_topics = {topic_type: self.soup.find_all(
            name='div', class_='topic-list-item-row')}
        self.asserted_topic_slugs = {topic_type: set()}

    def parse_as_archived_page_start(self) -> None:
        """
        Parse the resulted HTML as it's only one served page of a
        topic list, served through the api on page change.
        """
        self.listed_topic_categories = ['archived']
        self.listed_topics = {'archived': self.soup.find(
            name='section', class_='topic-list-wrapper').find_all(
            name='div', class_='topic-list-item-row')}
        self.asserted_topic_slugs = {'archived': set()}

    def _assert_topic_properties(
            self, topic: Tag, name_contains: str, username_contains: str,
            total_comments: int) -> None:
        """
        Assert the properties of a certain found topic
        """
        if name_contains is not None:
            # Assert the topic text
            topic_link = topic.find(class_='topic-link')  # type: Tag
            inner_html = self._get_inner_html(tag=topic_link)
            self.test.assertIn(
                member=name_contains, container=inner_html, msg=_(
                    'Listed topic name doesn\'t contain the expected '
                    'string.'))
        if username_contains is not None:
            # Assert the username text
            user_link = topic.find(class_='forum-username')  # type: Tag
            inner_html = self._get_inner_html(tag=user_link)
            self.test.assertIn(
                member=username_contains, container=inner_html, msg=_(
                    'Listed user name doesn\'t contain the expected string.'))
        if total_comments is not None:
            # Assert the total comments number
            comment_count_wrapper = topic.find(class_='topic-comment-count')
            inner_html = self._get_inner_html(tag=comment_count_wrapper)
            self.test.assertEqual(
                int(inner_html), total_comments,
                msg=_('Wrong number of comments found.'))

    def _get_slug(self, topic: Tag):
        """
        Return the slug for a rendered topic element.
        """
        topic_link = topic.find(class_='topic-link')  # type: Tag
        return topic_link['data-slug']

    def _look_for_a_topic(
            self, topics: List, topic_type: str, slug: str) -> List:
        """
        Look for and return a topic from the given category with a given
        slug.

        Return a `list` containing the topics with the given slug,
        normally it the list should contain only one item if found.
        """
        found_topics = []
        for topic in topics:  # type: Tag
            if self._get_slug(topic=topic) == slug:
                found_topics.append(topic)
        return found_topics

    def _assert_preview_contains(
            self, slug: str, preview_contains: str) -> None:
        """
        Assert that a given template with a preview comment exists for
        the passed `slug`.
        """
        if preview_contains is None:
            # Not looking for anything
            return
        tooltip_template = self.soup.find(
            name='template', class_='forum-topic-tooltip-template',
            attrs={'data-slug': slug})  # type: Tag
        tooltip_inner_html = self._get_inner_html(tag=tooltip_template.div)
        self.test.assertIn(
            member=preview_contains, container=tooltip_inner_html, msg=_(
                'Tooltip for \'{slug}\' does not contain expected string.'
            ).format(slug=slug))

    def assert_topic_listed(
            self, topic_type: str, slug: str, name_contains: str=None,
            username_contains: str=None, total_comments: int=None,
            preview_contains: str=None) -> None:
        """
        Assert that a certain topic is listed within a certain category
        and has the passed properties.
        """
        topics = self.listed_topics[topic_type]
        found_topics = self._look_for_a_topic(
            topics=topics, topic_type=topic_type, slug=slug)
        self.test.assertEqual(len(found_topics), 1, msg=_(
            'Topic with slug \'{slug}\' not found.').format(slug=slug))
        # At this point we have found the topic
        topic = found_topics[0]
        self._assert_topic_properties(
            topic=topic, name_contains=name_contains,
            username_contains=username_contains, total_comments=total_comments)
        self._assert_preview_contains(
            slug=slug, preview_contains=preview_contains)
        self.asserted_topic_slugs[topic_type].add(slug)

    def assert_topic_not_listed(self, topic_type: str, slug: str) -> None:
        """
        Assert that a passed slug is not listed in the given topic type
        HTML result.
        """
        topics = self.listed_topics[topic_type]
        found_topics = self._look_for_a_topic(
            topics=topics, topic_type=topic_type, slug=slug)
        self.test.assertEqual(len(found_topics), 0, msg=_(
            'Unexpected topic with slug \'{slug}\' in topic_type '
            '\'{topic_type}\'.').format(slug=slug, topic_type=topic_type))

    def assert_no_more_topics_listed(self):
        """
        Assert that within the test we looked up all the topics that
        are listed in the topic page.
        """
        for topic_type in self.listed_topic_categories:
            # Get the listed topic slugs
            topics_slugs_remaining = list(map(
                lambda x: self._get_slug(topic=x),
                self.listed_topics[topic_type]))
            for asserted_slug in self.asserted_topic_slugs[topic_type]:
                topics_slugs_remaining.remove(asserted_slug)
            self.test.assertEqual(
                len(topics_slugs_remaining), 0, msg=_(
                    'Extra formerly not asserted topics found at '
                    '\'{topic_type}\': {topics_slugs_remaining}').format(
                    topic_type=topic_type,
                    topics_slugs_remaining=topics_slugs_remaining))
