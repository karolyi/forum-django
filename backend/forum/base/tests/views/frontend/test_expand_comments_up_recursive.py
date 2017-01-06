from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from forum.testutils.html_result_parser import CommentsUpRecursiveParser


class ExpandCommentsUpRecursiveTestCase(TestCase):
    """
    Testing `expand_comments_up_recursive`.
    """

    fixtures = [
        'topic-tests-user', 'topic-tests-topic',
        'topic-tests-comments-staffonly', 'topic-tests-comments-normal']

    def test_disallow_staff_topic_for_anon(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic',
                'comment_id': 1,
                'scroll_to_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_http404_for_nonexistent_staff_comment_requested(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic',
                'comment_id': 999,
                'scroll_to_id': 789}))
        self.assertEqual(response.status_code, 404)

    def test_http404_for_nonexistent_topic_requested(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'i-do-no-exist',
                'comment_id': 1,
                'scroll_to_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_allow_staff_topic_for_staff(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        client.login(username='staffuser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic',
                'comment_id': 1,
                'scroll_to_id': 1}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        parser.assert_commentid_contains_content(
            comment_id=1,
            content='second staff html content id 1, a non-reply')
        parser.assert_no_more_comments()

    def test_allow_staff_topic_for_superuser(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic',
                'comment_id': 1,
                'scroll_to_id': 1}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        parser.assert_commentid_contains_content(
            comment_id=1,
            content='second staff html content id 1, a non-reply')
        parser.assert_no_more_comments()

    def test_allow_moved_comment_from_staff(self):
        """
        Allow showing a comment that's moved from a staff topic, to
        non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'normal-topic',
                'comment_id': 4,
                'scroll_to_id': 4}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        parser.assert_commentid_contains_content(
            comment_id=4,
            content='moved from staff html content id 3, a non-reply')
        parser.assert_no_more_comments()
