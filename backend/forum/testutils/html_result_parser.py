from collections import OrderedDict
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.http.response import HttpResponse
from django.test import TestCase
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from forum.base.choices import LIST_TOPIC_TYPE


class HTMLParserMixin(object):
    """
    Tools for generic HTML parsing.
    """


class HtmlResultParserBase(HTMLParserMixin):
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


class TimeParser(object):
    """
    Tester for a generated `time` tag.
    """

    def __init__(self, tag: Tag, test: TestCase):
        self.tag = tag
        self.test = test
        self.test.assertIsInstance(obj=tag, cls=Tag)

    def assert_value(self, value: str):
        """
        Assert that the `datetime` attribute has the passed value.
        """
        self.test.assertEqual(self.tag['datetime'], value, msg=_(
            'Date element\'s datetime attribute has the wrong value'))


class UserNameParser(object):
    """
    Tester for a generated forum username tag.
    """

    def __init__(self, tag: Tag, test: TestCase):
        self.tag = tag
        self.test = test
        self.test.assertIsInstance(obj=tag, cls=Tag)

    def assert_slug(self, value: str=None):
        """
        Assert that the slug in the username tag is the expected one.
        """
        if value is not None:
            self.test.assertEqual(self.tag['data-slug'], value, msg=_(
                'Username has the wrong slug'))

    def assert_text(self, value: str=None):
        """
        Assert that the username contains the expected value.
        """
        if value is not None:
            self.test.assertEqual(self.tag.decode_contents(), value, msg=_(
                'Username has the wrong text'))


class OneTopicCommentParser(HTMLParserMixin):
    """
    Functionality for testing out one rendered topic comment structure.
    """

    def __init__(self, comment: Tag, test: TestCase):
        self.comment = comment
        self.test = test
        self._asserted_replies = []

    @cached_property
    def _comment_content(self) -> Tag:
        """
        Return the comment content tag.
        """
        comment_content = \
            self.comment.find(name='div', class_='comment-content')
        self.test.assertIsInstance(obj=comment_content, cls=Tag)
        return comment_content

    @cached_property
    def _replies(self):
        """
        Return the replies to this comment in an array.
        """
        return self._comment_content.find_all(
            name='div', class_='topic-comment-onereply', recursive=False)

    @cached_property
    def _reply_ids(self):
        reply_ids = []
        for reply in self._replies:  # type: Tag
            link_to = int(reply.find(
                name='a', class_='to-reply-comment')['data-link-to'])
            reply_ids.append(link_to)
        return reply_ids

    @cached_property
    def _id(self) -> int:
        """
        Return the ID of the rendered comment.
        """
        return int(self.comment['data-comment-id'])

    def __str__(self):
        """
        Return a readable name.
        """
        return _(
            '<OneTopicCommentParser with comment ID {id}>').format(id=self._id)

    def assert_number(self, number: int):
        """
        Assert that the comment ID is the expected one.
        """
        comment_number_wrapper = self.comment.find(
            name='div', class_='comment-number-wrapper')  # type: Tag
        self.test.assertIsInstance(obj=comment_number_wrapper, cls=Tag, msg=_(
            'Wrapper for the comment number not found'))
        comment_link = comment_number_wrapper.a.span  # type: Tag
        self.test.assertIsInstance(obj=comment_link, cls=Tag, msg=_(
            'Comment number link not found'))
        content = comment_link.decode_contents()
        comment_number = '#{value}'.format(value=number)
        content = '#{content}'.format(content=content)
        self.test.assertEqual(content, comment_number, msg=_(
            'Comment number is not the expected'))

    def assert_user(self, user_slug: str, username: str=None):
        """
        Assert that the poster is the expected username.
        """
        commenter_wrapper = self.comment.find(
            name='div', class_='commenter-user')  # type: Tag
        self.test.assertIsInstance(obj=commenter_wrapper, cls=Tag, msg=_(
            'Commenter wrapper HTML Tag not found.'))
        username_parser = UserNameParser(
            tag=commenter_wrapper.a, test=self.test)
        username_parser.assert_slug(value=user_slug)
        username_parser.assert_text(value=username)

    def assert_contains_content(self, content: str):
        """
        Assert that the comment contains the given content.
        """
        self.test.assertIn(
            member=content, container=self._comment_content.decode_contents())

    def assert_no_previous(self):
        """
        Assert that a comment is not a reply to another one.
        """

        previous_wrapper = self.comment.find(
            name='div', class_='comment-previous')
        for item in previous_wrapper.children:
            self.test.assertNotIsInstance(obj=item, cls=Tag, msg=_(
                'HTML Tag found where none expected.'))

    def assert_previous(
            self, comment_id: int, user_slug: str=None, username: str=None,
            number: int=None):
        """
        Assert that a comment is not a reply to another one.
        """

        previous_wrapper = self.comment.find(
            name='div', class_='comment-previous')  # type: Tag
        previous_link = previous_wrapper.a  # type: Tag
        self.test.assertIsInstance(obj=previous_link, cls=Tag, msg=_(
            'Previous comment expected but not found'))
        self.test.assertEqual(
            int(previous_link['data-link-to']), comment_id, msg=_(
                'Previous comment ID differs from expected'))
        if number is not None:
            content = previous_link.decode_contents()
            prev_number = content[content.rfind('#'):]
            str_number = '#{number}'.format(number=number)
            self.test.assertEqual(prev_number, str_number, msg=_(
                'Previous comment number differs from expected'))
        user_parser = UserNameParser(
            tag=previous_wrapper.find(name='a', class_='forum-username'),
            test=self.test)
        user_parser.assert_slug(value=user_slug)
        user_parser.assert_text(value=username)

    def assert_reply(
            self, comment_id: int, user_slug: str=None, username: str=None,
            number: int=None):
        """
        Assert that the comment has a reply by a given user slug and a
        given comment id.
        """
        self.test.assertGreater(len(self._replies), 0, msg=_(
            'Asserted a reply where there is none'))
        for reply in self._replies:  # type: Tag
            username_link = reply.find(name='a', class_='forum-username')
            comment_link = reply.find(name='a', class_='to-reply-comment')
            link_to = int(comment_link['data-link-to'])
            if link_to == comment_id:
                break
        else:
            self.test.fail(_(
                'Reply with comment ID {comment_id} not found.').format(
                comment_id=comment_id))
        if number is not None:
            content = comment_link.span.decode_contents()
            content = '#{content}'.format(content=content)
            str_number = '#{number}'.format(number=number)
            self.test.assertEqual(content, str_number, msg=_(
                'Reply comment number differs from expected'))
        user_parser = UserNameParser(tag=username_link, test=self.test)
        user_parser.assert_slug(value=user_slug)
        user_parser.assert_text(value=username)
        self._asserted_replies.append(link_to)

    def assert_no_replies(self):
        """
        Assert that there are no replies to this comment.
        """
        self.test.assertEqual(len(self._replies), 0, msg=_(
            'Replies with ID {ids} found where none expected').format(
            ids=', '.join(map(str, self._reply_ids))))

    def assert_replies_order(self):
        """
        Assert that the previously checked replies are in their check
        order.
        """
        self.test.assertListEqual(
            self._reply_ids, self._asserted_replies, msg=_(
                'Asserted the second order, got the first'))

    def assert_vote_value(self, value: int):
        """
        Assert the votes value on the renderes comment.
        """
        value_wrapper = self.comment.find(
            name='div', class_='voting-value-wrapper')
        self.test.assertIsInstance(value_wrapper, Tag)
        value_html = value_wrapper.find(
            name='span', class_='voting-value').decode_contents()
        value_int = int(value_html)
        self.test.assertEqual(value_int, value, msg=_(
            'Comment votes value differs from expected'))

    def assert_time(self, value: str):
        """
        Assert that the comment has the passed time identifier.
        """
        comment_time = self.comment.find(name='div', class_='comment-time')
        time_parser = TimeParser(
            tag=comment_time.time, test=self.test)
        time_parser.assert_value(value=value)


class CommentsPageParser(HtmlResultParserBase):
    """
    A base class for parsing rendered comments.
    """

    def __init__(self, *args, **kwargs):
        super(CommentsPageParser, self).__init__(*args, **kwargs)

        self.rendered_comments = OrderedDict()
        self.last_cached_comment = None

    def assert_and_return_commentid(self, comment_id: int):
        """
        Assert that a given comment ID exists and return an initialized
        `OneTopicCommentParser` for it, for further parsing.
        """
        comment_wrapper = self.soup.main.article.find(
            name='section', attrs={'data-comment-id': comment_id})
        self.test.assertIs(type(comment_wrapper), Tag, msg=_(
            'Comment with ID {id} not found').format(id=comment_id))
        self.rendered_comments[comment_id] = comment_wrapper
        self.last_cached_comment = comment_wrapper
        return OneTopicCommentParser(
            comment=comment_wrapper, test=self.test)

    def assert_no_more_comments_and_order(self) -> None:
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
        id_list_extra_ids = id_list.copy()
        for comment_id in self.rendered_comments.keys():
            id_list_extra_ids.remove(comment_id)
        if id_list_extra_ids:
            self.test.fail(msg=_(
                'There are extra unasserted comments with IDs {ids}').format(
                ids=', '.join(map(str, id_list_extra_ids))))
        self.test.assertListEqual(
            id_list, list(self.rendered_comments.keys()), msg=_(
                'Expected the order of IDs to be the first, got the second'))


class ExpandedThreadParser(CommentsPageParser):
    """
    Parsing the result of `comments_up_recursive` view.
    """

    def __init__(self, *args, **kwargs) -> None:
        super(ExpandedThreadParser, self).__init__(*args, **kwargs)

    def _get_topic_group_wrappers(
            self, first: OneTopicCommentParser, second: OneTopicCommentParser):
        """
        Extract the topic group wrappers from two given comments.
        """
        parents = []
        for item in [first, second]:
            for parent in item.comment.parents:
                if 'group-comments-in-topic' in parent.get('class', []):
                    parents.append(parent)
                    break
            else:
                self.test.fail(msg=_(
                    'Topic wrapper not found for comment ID {comment_id}'
                ).format(comment_id=item._id))
        return parents

    def assert_same_topicgroup_tag(
            self, first: OneTopicCommentParser, second: OneTopicCommentParser):
        """
        Assert that the topic group wrappers are the same `Tag`s for the
        two passed `OneTopicCommentParser` classes.
        """
        parents = self._get_topic_group_wrappers(first=first, second=second)
        if parents[0] != parents[1]:
            self.test.fail(msg=_(
                'Parent Tags for {first} and {second} expected to be the same '
                'but they aren\'t').format(
                first=first, second=second))

    def assert_different_topicgroup(
            self, first: OneTopicCommentParser, second: OneTopicCommentParser):
        """
        Assert that the passed comments are rendered in different topic
        group wrappers.
        """
        parents = self._get_topic_group_wrappers(first=first, second=second)
        slug_1 = parents[0]['data-topic-slug']
        if parents[0] == parents[1]:
            self.test.fail(msg=_(
                'Parents for {first} and {second} expected to be different '
                'but they are the same HTML Tag with slug: {slug}').format(
                first=first, second=second, slug=slug_1))
        slug_2 = parents[1]['data-topic-slug']
        if slug_1 == slug_2:
            self.test.fail(msg=_(
                'Parents for {first} and {second} expected to be different '
                'Tags, they are but group the same topic: {slug}').format(
                first=first, second=second, slug=slug_1))


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
            self.listed_topics[topic_type] = self.soup.main.find(
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
            self, topic: Tag, topic_name: str, username: str,
            total_comments: int) -> None:
        """
        Assert the properties of a certain found topic
        """
        if topic_name is not None:
            # Assert the topic text
            topic_link = topic.find(class_='topic-link')  # type: Tag
            inner_html = topic_link.decode_contents()
            self.test.assertEquals(
                inner_html, topic_name, msg=_(
                    'Listed topic name isn\'t the expected string.'))
        if username is not None:
            # Assert the username text
            user_parser = UserNameParser(
                tag=topic.find(class_='forum-username'), test=self.test)
            user_parser.assert_text(value=username)
        if total_comments is not None:
            # Assert the total comments number
            comment_count_wrapper = topic.find(
                class_='topic-comment-count')  # type: Tag
            inner_html = comment_count_wrapper.decode_contents()
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
        tooltip_inner_html = tooltip_template.div.decode_contents()
        self.test.assertIn(
            member=preview_contains, container=tooltip_inner_html, msg=_(
                'Tooltip for \'{slug}\' does not contain expected string.'
            ).format(slug=slug))

    def assert_topic_listed(
            self, topic_type: str, slug: str, topic_name: str=None,
            username: str=None, total_comments: int=None,
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
            topic=topic, topic_name=topic_name, username=username,
            total_comments=total_comments)
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
