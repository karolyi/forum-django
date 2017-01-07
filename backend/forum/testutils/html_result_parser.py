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
        self.test.assertIn(
            member=content,
            container=self.last_cached_comment.find(
                name='div', class_='comment-content').text)

    def assert_its_content_contains(self, content: str) -> None:
        """
        Assert that the lastly used comment wrapper contains the given
        content.
        """
        self.test.assertIn(
            member=content,
            container=self.last_cached_comment.find(
                name='div', class_='comment-content').text)

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
        self._remove_templates()
        self._fetch_topics()
        self.asserted_topic_slugs = {
            topic_type: set() for topic_type in LIST_TOPIC_TYPE}

    def _fetch_topics(self) -> None:
        """
        Build the list of topics.
        """
        self.listed_topics = {
            topic_type: [] for topic_type in LIST_TOPIC_TYPE}
        for topic_type in LIST_TOPIC_TYPE:
            self.listed_topics[topic_type] = \
                self.soup.main.find(
                    name='div',
                    class_='topic-type-{topic_type}'.format(
                        topic_type=topic_type)).find_all(
                    name='div', class_='topic-list-item-row')

    def _assert_topic_properties(
            self, topic: Tag, name_contains: str, username_contains: str,
            total_comments: int) -> None:
        """
        Assert the properties of a certain found topic
        """
        if name_contains is not None:
            # Assert the topic text
            topic_link = topic.find(class_='topic-link')  # type: Tag
            self.test.assertIn(member=name_contains, container=topic_link.text)
        if username_contains is not None:
            # Assert the username text
            user_link = topic.find(class_='forum-username')  # type: Tag
            self.test.assertIn(
                member=username_contains, container=user_link.text)
        if total_comments is not None:
            # Assert the total comments number
            comment_count_wrapper = topic.find(class_='topic-comment-count')
            self.test.assertEqual(
                int(comment_count_wrapper.text), total_comments,
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

    def assert_topic_listed(
            self, topic_type: str, slug: str, name_contains: str=None,
            username_contains: str=None, total_comments: int=None) -> None:
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
            'Expected a topic to not be found but found a topic with a slug '
            '{slug} in topic_type {topic_type}').format(
            slug=slug, topic_type=topic_type))

    def assert_no_more_topics_listed(self):
        """
        Assert that within the test we looked up all the topics that
        are listed in the topic page.
        """
        for topic_type in LIST_TOPIC_TYPE:
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
