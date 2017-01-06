import copy

from bs4 import BeautifulSoup
from bs4.element import Tag
from django.http.response import HttpResponse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _


class HtmlResultParserBase(object):
    """
    Tool for parsing the rendered HTML content with end-to-end testing.
    """

    def __init__(self, test: TestCase, response: HttpResponse):
        """
        Store the passed `TestCase` object into self, for later asserts.
        """
        self.test = test
        self.response = response

    def _assert_statuscode_200(self):
        self.test.assertEqual(self.response.status_code, 200)

    def parse_result(self):
        """
        Parse the response output to `BeautifulSoup` structure.
        """
        markup = self.response.content.decode('utf-8')
        self.soup = BeautifulSoup(markup=markup, features='lxml')


class CommentsUpRecursiveParser(HtmlResultParserBase):
    """
    Parsing the result of `comments_up_recursive` view.
    """

    def __init__(self, test: TestCase, response: HttpResponse):
        super(CommentsUpRecursiveParser, self).__init__(
            test=test, response=response)
        self._assert_statuscode_200()
        self.parse_result()
        self.rendered_comments = {}
        self.last_cached_comment = None

    def assert_commentid_contains_content(
            self, comment_id: int, content: str):
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

    def assert_its_content_contains(self, content: str):
        """
        Assert that the lastly used comment wrapper contains the given
        content.
        """
        self.test.assertIn(
            member=content,
            container=self.last_cached_comment.find(
                name='div', class_='comment-content').text)

    def assert_no_more_comments(self):
        """
        Assert that only the previously looked up comments are rendered
        in the HTML response.
        """
        article_copy = copy.copy(self.soup.main.article)  # type: Tag
        self.test.assertIs(type(article_copy), Tag)
        template = article_copy.template
        # Remove ALL the templates!
        while template is not None:
            article_copy.template.decompose()
            template = article_copy.template
        rendered_comments = article_copy.find_all(
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
