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
        'topic-tests-comments-archived', 'topic-tests-topic-normal-extra',
        'topic-tests-comments-normal-extra']

    def _get_parser(self, response: HttpResponse) -> TopicListingParser:
        """
        Start and return the parser for each test case.
        """
        parser = TopicListingParser(test=self, response=response)
        parser.parse_as_one_topic_page(topic_type='normal')
        return parser

    def test_emits_404_for_wrong_topic_type(self):
        """
        Should return HTTP 404 for a wrong `topic_type` parameter.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
                'topic_type': 'foo', 'page_id': '1'})  # type: HttpResponse
        self.assertEqual(response.status_code, 404)

    def test_emits_404_for_missing_topic_type(self):
        """
        Should return HTTP 404 for a missing `topic_type` parameter.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
                'page_id': '1'})  # type: HttpResponse
        self.assertEqual(response.status_code, 404)

    def test_emits_404_for_missing_page_id(self):
        """
        Should return HTTP 404 for a missing `page_id` parameter.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
                'topic_type': 'normal'})  # type: HttpResponse
        self.assertEqual(response.status_code, 404)

    def test_emits_404_for_non_int_page_id(self):
        """
        Should return HTTP 404 for garbage in the `page_id` parameter.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
                'topic_type': 'normal',
                'page_id': 'non-int-value'})  # type: HttpResponse
        self.assertEqual(response.status_code, 404)

    def test_emits_404_for_nonexistent_page(self):
        """
        Assert that we get a 404 for a topic list page that's
        nonexistent.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
            'topic_type': 'normal', 'page_id': 50})
        self.assertEqual(response.status_code, 404)

    def test_shows_page_1(self):
        """
        Assert that when requested the first page, only the topics on
        that page are returned in the HTML.

        This test takes the shown pages value from the client's
        session data.
        """
        client = Client()
        # To modify the session and then save it, it must be stored in a
        # variable first (because a new SessionStore is created every
        # time this property is accessed):
        session = client.session
        session['topics_per_page'] = 2
        session.save()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
            'topic_type': 'normal', 'page_id': 1})
        parser = self._get_parser(response=response)
        parser.assert_topic_listed(
            topic_type='normal', slug='normal-topic-5',
            topic_name='Normal topic 5 html name', username='SuperUser',
            total_comments=1,
            preview_contains='Normal topic 5 first comment HTML')
        parser.assert_topic_listed(
            topic_type='normal', slug='normal-topic-4',
            topic_name='Normal topic 4 html name', username='StaffUser',
            total_comments=1,
            preview_contains='Normal topic 4 first comment HTML')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-3')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-2')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-1')
        parser.assert_no_more_topics_listed()

    def test_shows_page_2(self):
        """
        Assert that when requested the second page, only the topics on
        that page are returned in the HTML.

        This test takes the shown pages value from the client's
        session data.
        """
        client = Client()
        # To modify the session and then save it, it must be stored in a
        # variable first (because a new SessionStore is created every
        # time this property is accessed):
        session = client.session
        session['topics_per_page'] = 2
        session.save()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
            'topic_type': 'normal', 'page_id': 2})
        parser = self._get_parser(response=response)
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-5')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-4')
        parser.assert_topic_listed(
            topic_type='normal', slug='normal-topic-3',
            topic_name='<b>Normal topic 3 html name</b>',
            username='InactiveUser', total_comments=1,
            preview_contains='Normal topic 3 first comment HTML')
        parser.assert_topic_listed(
            topic_type='normal', slug='normal-topic-2',
            topic_name='Normal topic 2 html name',
            username='ValidUser', total_comments=1,
            preview_contains='<b>Normal topic 2 first comment HTML</b>')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-1')
        parser.assert_no_more_topics_listed()

    def test_shows_page_3(self):
        """
        Assert that when requested the third page, only the topics on
        that page are returned in the HTML.

        This test takes the shown pages value from the client's
        session data.
        """
        client = Client()
        # To modify the session and then save it, it must be stored in a
        # variable first (because a new SessionStore is created every
        # time this property is accessed):
        session = client.session
        session['topics_per_page'] = 2
        session.save()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
            'topic_type': 'normal', 'page_id': 3})
        parser = self._get_parser(response=response)
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-5')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-4')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-3')
        parser.assert_topic_not_listed(
            topic_type='normal', slug='normal-topic-2')
        parser.assert_topic_listed(
            topic_type='normal', slug='normal-topic-1',
            topic_name='Normal topic 1 html name',
            username='InactiveUser', total_comments=1,
            preview_contains='moved from staff html content id 3, a non-reply')
        parser.assert_no_more_topics_listed()

    def test_emits_404_for_page_4(self):
        """
        Assert that when requested the fourt page, we get a 404 since
        there's not a fourth page with `topics_per_page = 2`.

        This test takes the shown pages value from the client's
        session data.
        """
        client = Client()
        # To modify the session and then save it, it must be stored in a
        # variable first (because a new SessionStore is created every
        # time this property is accessed):
        session = client.session
        session['topics_per_page'] = 2
        session.save()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-topic-list-page'), data={
            'topic_type': 'normal', 'page_id': 4})
        self.assertEqual(response.status_code, 404)
