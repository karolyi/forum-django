# from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.test import TestCase
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
        parser.parse_full_page()
        return parser
