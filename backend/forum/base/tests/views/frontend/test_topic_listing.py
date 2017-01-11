from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.test import Client, TestCase
from forum.testutils.html_result_parser import TopicListingParser


class TopicListingTestCase(TestCase):
    """
    Testing `topic_listing`.
    """
    fixtures = [
        'topic-tests-user', 'topic-tests-topic', 'topic-tests-topic-archived',
        'topic-tests-comments-staffonly', 'topic-tests-comments-normal',
        'topic-tests-comments-highlighted', 'topic-tests-comments-disabled',
        'topic-tests-comments-archived']

    def _get_parser(self, response: HttpResponse) -> TopicListingParser:
        """
        Start and return the parser for each test case.
        """
        parser = TopicListingParser(test=self, response=response)
        parser.parse_as_full_page()
        return parser

    def assert_topics_for_everyone(self, response: HttpResponse) -> None:
        """
        Certain topics will be listed for everyone, assert them here.
        """
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='highlighted',
            topic_name='Highlighted topic 1 html name',
            slug='highlighted-topic-1', username='StaffUser',
            total_comments=3,
            preview_contains='Highlighted topic html content id 7, a reply '
            'to 5')
        parser.assert_topic_listed(
            topic_type='normal', topic_name='Normal topic 1 html name',
            slug='normal-topic-1', username='InactiveUser',
            total_comments=1,
            preview_contains='moved from staff html content id 3, a non-reply')
        parser.assert_topic_not_listed(topic_type='highlighted', slug='foo')
        parser.assert_no_more_topics_listed()

    def assert_topics_for_staff(self, response: HttpResponse) -> None:
        """
        Assert that the rendered topics contain the ones only visible
        for staff.
        """
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='normal', topic_name='Staff only topic 1 html name',
            slug='staff-only-topic-1', username='SuperUser',
            total_comments=4,
            preview_contains='fourth staff html content id 9, a reply to 2')
        parser.assert_topic_listed(
            topic_type='highlighted',
            topic_name='Highlighted topic 1 html name',
            slug='highlighted-topic-1', username='StaffUser',
            total_comments=3,
            preview_contains='Highlighted topic html content id 7, a reply '
            'to 5')
        parser.assert_topic_listed(
            topic_type='normal', topic_name='Normal topic 1 html name',
            slug='normal-topic-1', username='InactiveUser',
            total_comments=1,
            preview_contains='moved from staff html content id 3, a non-reply')
        parser.assert_topic_not_listed(topic_type='highlighted', slug='foo')
        parser.assert_no_more_topics_listed()

    def test_renders_topics_properly_for_anonymous(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        self.assert_topics_for_everyone(response=response)

    def test_renders_topics_properly_for_non_staff(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        self.assert_topics_for_everyone(response=response)

    def test_renders_topics_properly_for_staff(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='StaffUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        self.assert_topics_for_staff(response=response)

    def test_renders_topics_properly_for_superuser(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        self.assert_topics_for_staff(response=response)

    def test_renders_topics_properly_for_superstaffuser(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='SuperStaffUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        self.assert_topics_for_staff(response=response)

    def test_renders_topics_properly_for_archivesexpanderuser(self):
        """
        Assert that the topics in the fixtures do render properly.
        """
        client = Client()
        client.login(username='ArchivesExpanderUser', password='ValidPassword')
        response = client.get(reverse(viewname='forum:base:topic-listing'))
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='highlighted',
            topic_name='Highlighted topic 1 html name',
            slug='highlighted-topic-1', username='StaffUser',
            total_comments=3,
            preview_contains='Highlighted topic html content id 7, a reply '
            'to 5')
        parser.assert_topic_listed(
            topic_type='normal', topic_name='Normal topic 1 html name',
            slug='normal-topic-1', username='InactiveUser',
            total_comments=1,
            preview_contains='moved from staff html content id 3, a non-reply')
        parser.assert_topic_listed(
            topic_type='archived',
            topic_name='Archived enabled non-staff topic 1 html name',
            slug='archived-enabled-non-staff-topic-1',
            username='SuperStaffUser', total_comments=2,
            preview_contains='Archived enabled non-staff second comment HTML')
        parser.assert_topic_not_listed(topic_type='highlighted', slug='foo')
        parser.assert_no_more_topics_listed()
