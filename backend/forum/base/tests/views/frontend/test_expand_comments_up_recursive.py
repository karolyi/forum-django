from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from forum.testutils.html_result_parser import CommentsUpRecursiveParser


class BasicTestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with basic tests.
    """

    fixtures = [
        'topic-tests-user', 'topic-tests-topic',
        'topic-tests-comments-staffonly', 'topic-tests-comments-normal',
        'topic-tests-comments-highlighted', 'topic-tests-comments-disabled']

    def test_disallow_staff_topic_for_anon(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 1,
                'scroll_to_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_disallow_staff_topic_for_anon_instead_redirect(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.

        When the user would except a redirect (thus finding out the
        topic slug assigned a given comment), don't allow that and
        assert a redirect.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic-1cccccc',
                'comment_id': 1,
                'scroll_to_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_redirect_staff_topic_with_wrong_slug_valid_id(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.

        If the user is able to see the requested topic but passes the
        wrong slug, redirect him to the correct slug.
        """
        client = Client()
        client.login(username='staffuser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic-1cccccc',
                'comment_id': 1,
                'scroll_to_id': 2}))
        # Assert a permanent redirect
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.get('Location'), reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 1,
                'scroll_to_id': 2}))

    def test_http404_for_nonexistent_staff_comment_requested(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'staff-only-topic-1',
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
                'topic_slug': 'staff-only-topic-1',
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
                'topic_slug': 'staff-only-topic-1',
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
                'topic_slug': 'normal-topic-1',
                'comment_id': 4,
                'scroll_to_id': 4}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        parser.assert_commentid_contains_content(
            comment_id=4,
            content='moved from staff html content id 3, a non-reply')
        parser.assert_no_more_comments()


class Scenario1TestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with test scenario 1.
    """

    fixtures = [
        'topic-tests-user',
        'comment-tests-topics-scenario-1',
        'comment-tests-comments-scenario-1']

    def test_shows_expansion_to_anon_properly(self):
        """
        Should list the appropriate comment thread for `AnonymousUser`.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 100,
                'scroll_to_id': 100}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        parser.assert_commentid_contains_content(
            comment_id=100,
            content='comment ID 100 HTML content')
        # parser.assert_no_more_comments()
