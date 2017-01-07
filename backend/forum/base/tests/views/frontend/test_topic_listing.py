from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from forum.testutils.html_result_parser import TopicListingParser


class TopicListingTestCase(TestCase):
    """
    Testing `topic_listing`.
    """
    fixtures = [
        'topic-tests-user', 'topic-tests-topic',
        'topic-tests-comments-staffonly', 'topic-tests-comments-normal',
        'topic-tests-comments-highlighted', 'topic-tests-comments-disabled']

    def assert_topics_for_everyone(self, parser: TopicListingParser) -> None:
        """
        Certain topics will be listed for everyone, assert them here.
        """
        parser.assert_topic_listed(
            topic_type='highlighted', name_contains='Highlighted topic 1',
            slug='highlighted-topic-1', username_contains='StaffUser',
            total_comments=3)
        parser.assert_topic_listed(
            topic_type='normal', name_contains='Normal topic 1',
            slug='normal-topic-1', username_contains='InactiveUser',
            total_comments=1)
        parser.assert_topic_not_listed(topic_type='highlighted', slug='foo')
        parser.assert_no_more_topics_listed()

    def test_renders_topics_properly_for_anonymous(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = TopicListingParser(test=self, response=response)
        self.assert_topics_for_everyone(parser=parser)

    def test_renders_topics_properly_for_non_staff(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = TopicListingParser(test=self, response=response)
        self.assert_topics_for_everyone(parser=parser)

    def test_renders_topics_properly_for_staff(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='StaffUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = TopicListingParser(test=self, response=response)
        parser.assert_topic_listed(
            topic_type='normal', name_contains='Staff only topic 1',
            slug='staff-only-topic-1', username_contains='SuperUser',
            total_comments=4)
        self.assert_topics_for_everyone(parser=parser)

    def test_renders_topics_properly_for_superuser(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = TopicListingParser(test=self, response=response)
        parser.assert_topic_listed(
            topic_type='normal', name_contains='Staff only topic 1',
            slug='staff-only-topic-1', username_contains='SuperUser',
            total_comments=4)
        self.assert_topics_for_everyone(parser=parser)

    def test_renders_topics_properly_for_superstaffuser(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='SuperStaffUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = TopicListingParser(test=self, response=response)
        parser.assert_topic_listed(
            topic_type='normal', name_contains='Staff only topic 1',
            slug='staff-only-topic-1', username_contains='SuperUser',
            total_comments=4)
        self.assert_topics_for_everyone(parser=parser)
