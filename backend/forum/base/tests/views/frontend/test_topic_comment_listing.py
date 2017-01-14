from django.test import Client, TestCase
from django.urls.base import reverse
from forum.testutils.html_result_parser import CommentsPageParser

VIEWNAME = 'forum:base:topic-comment-listing'


class BasicTestCase(TestCase):
    """
    Testing `topic_comment_listing` with basic tests.
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
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1'}))
        self.assertEqual(response.status_code, 404)

    def test_disallow_staff_topic_for_anon_instead_redirecting(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.

        When the user would except a redirect (thus finding out the
        topic slug assigned a given comment), don't allow that and
        assert a redirect.
        """
        client = Client()
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1cccccc',
                'comment_id': 1}))
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
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1cccccc',
                'comment_id': 1}))
        # Assert a permanent redirect
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.get('Location'), reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 1}))

    def test_http404_for_nonexistent_staff_comment_requested(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 999}))
        self.assertEqual(response.status_code, 404)

    def test_http404_for_nonexistent_topic_requested(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'i-do-no-exist',
                'comment_id': 1}))
        self.assertEqual(response.status_code, 404)

    def test_allow_staff_topic_for_staff(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        client.login(username='staffuser', password='ValidPassword')
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 1}))
        parser = CommentsPageParser(test=self, response=response)
        parser.assert_and_return_commentid(comment_id=9)
        parser.assert_and_return_commentid(comment_id=3)
        comment = parser.assert_and_return_commentid(comment_id=1)
        comment.assert_contains_content(
            content='second staff html content id 1, a non-reply')
        parser.assert_and_return_commentid(comment_id=2)
        parser.assert_no_more_comments_and_order()

    def test_allow_staff_topic_for_superuser(self):
        """
        Comment 1 in topic 1 cannot be expanded for non-staff users.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'staff-only-topic-1',
                'comment_id': 1}))
        parser = CommentsPageParser(test=self, response=response)
        parser.assert_and_return_commentid(comment_id=9)
        parser.assert_and_return_commentid(comment_id=3)
        comment = parser.assert_and_return_commentid(comment_id=1)
        comment.assert_contains_content(
            content='second staff html content id 1, a non-reply')
        parser.assert_and_return_commentid(comment_id=2)
        parser.assert_no_more_comments_and_order()

    def test_allow_moved_comment_from_staff(self):
        """
        Allow showing a comment that's moved from a staff topic, to
        non-staff users.
        """
        client = Client()
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'normal-topic-1',
                'comment_id': 4}))
        parser = CommentsPageParser(test=self, response=response)
        comment = parser.assert_and_return_commentid(comment_id=4)
        comment.assert_contains_content(
            content='moved from staff html content id 3, a non-reply')
        parser.assert_no_more_comments_and_order()

    def assert_disabled_topic_returns_404_for_client(self, client: Client):
        """
        Assert that requesting a disallowed topic returns a HTTP 404.
        """
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'disabled-normal-topic-1',
                'comment_id': 8}))
        self.assertEqual(response.status_code, 404)

    def assert_disabled_topic_returns_404_without_redirect(
            self, client: Client):
        """
        A comment in a disabled topic as a start comment should result
        in a HTTP 404 for `AnonymousUser`, and not a HTTP redirect, so
        the user would NOT be able to find out the disabled topic slug.
        """
        response = client.get(reverse(
            viewname=VIEWNAME, kwargs={
                'topic_slug': 'foo-topic',
                'comment_id': 8}))
        self.assertEqual(response.status_code, 404)

    def test_disallow_disabled_topic_for_all_usertype(self):
        """
        A comment in a disabled topic as a start comment should result
        in a HTTP 404 for `AnonymousUser`.
        """
        usertypes = [
            '', 'ValidUser', 'StaffUser', 'SuperUser', 'SuperStaffUser']
        for username in usertypes:
            client = Client()
            if username != '':
                client.login(username=username, password='ValidPassword')
            self.assert_disabled_topic_returns_404_for_client(client=client)
            self.assert_disabled_topic_returns_404_without_redirect(
                client=client)
