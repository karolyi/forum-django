from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.test import Client, TestCase
from forum.testutils.html_result_parser import TopicListingParser


class V1TopicListPageTestCase(TestCase):
    """
    Testing `v1_topic_list_page`.
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
        parser.parse_as_archived_page_start()
        return parser

    def test_lists_topics_for_anonymous(self):
        """
        Should lists topics for `AnonymousUser`.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-archived-topics-start'))
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled non-staff topic 1 html name',
            slug='archived-enabled-non-staff-topic-1',
            username_contains='SuperStaffUser',
            total_comments=2,
            preview_contains='Archived enabled non-staff second comment HTML')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-non-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-enabled-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-staff-topic-1')
        parser.assert_no_more_topics_listed()

    def test_lists_topics_for_valid_user(self):
        """
        Should lists topics for `ValidUser`.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:rest-api:v1-archived-topics-start'))
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled non-staff topic 1 html name',
            slug='archived-enabled-non-staff-topic-1',
            username_contains='SuperStaffUser',
            total_comments=2,
            preview_contains='Archived enabled non-staff second comment HTML')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-non-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-enabled-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-staff-topic-1')
        parser.assert_no_more_topics_listed()

    def test_lists_topics_for_staff_user(self):
        """
        Should lists topics for `StaffUser`.
        """
        client = Client()
        client.login(username='StaffUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:rest-api:v1-archived-topics-start'))
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled non-staff topic 1 html name',
            slug='archived-enabled-non-staff-topic-1',
            username_contains='SuperStaffUser',
            total_comments=2,
            preview_contains='Archived enabled non-staff second comment HTML')
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled staff topic 1 html name',
            slug='archived-enabled-staff-topic-1',
            username_contains='StaffUser',
            total_comments=1,
            preview_contains='Archived enabled staff first comment HTML')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-non-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-staff-topic-1')
        parser.assert_no_more_topics_listed()

    def test_lists_topics_for_superuser(self):
        """
        Should lists topics for `SuperUser`.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:rest-api:v1-archived-topics-start'))
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled non-staff topic 1 html name',
            slug='archived-enabled-non-staff-topic-1',
            username_contains='SuperStaffUser',
            total_comments=2,
            preview_contains='Archived enabled non-staff second comment HTML')
        parser.assert_topic_listed(
            topic_type='archived',
            name_contains='Archived enabled staff topic 1 html name',
            slug='archived-enabled-staff-topic-1',
            username_contains='StaffUser',
            total_comments=1,
            preview_contains='Archived enabled staff first comment HTML')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-non-staff-topic-1')
        parser.assert_topic_not_listed(
            topic_type='archived', slug='archived-disabled-staff-topic-1')
        parser.assert_no_more_topics_listed()
