from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
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

    def test_disallow_staff_topic_for_anon_instead_redirecting(self):
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
        comment = parser.assert_and_return_commentid(comment_id=1)
        comment.assert_contains_content(
            content='second staff html content id 1, a non-reply')
        parser.assert_no_more_comments_and_order()

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
        comment = parser.assert_and_return_commentid(comment_id=1)
        comment.assert_contains_content(
            content='second staff html content id 1, a non-reply')
        parser.assert_no_more_comments_and_order()

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
        comment = parser.assert_and_return_commentid(comment_id=4)
        comment.assert_contains_content(
            content='moved from staff html content id 3, a non-reply')
        parser.assert_no_more_comments_and_order()

    def assert_disabled_topic_returns_404_for_client(self, client: Client):
        """
        Assert that requesting a disallowed topic returns a HTTP 404.
        """
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'disabled-normal-topic-1',
                'comment_id': 8,
                'scroll_to_id': 8}))
        self.assertEqual(response.status_code, 404)

    def assert_disabled_topic_returns_404_without_redirect(
            self, client: Client):
        """
        A comment in a disabled topic as a start comment should result
        in a HTTP 404 for `AnonymousUser`, and not a HTTP redirect, so
        the user would NOT be able to find out the disabled topic slug.
        """
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'foo-topic',
                'comment_id': 8,
                'scroll_to_id': 8}))
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


class Scenario1Test1TestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with test scenario 1-1,
    testing expansion from comment 100.
    """

    fixtures = [
        'topic-tests-user',
        'comment-tests-topics-scenario-1',
        'comment-tests-comments-scenario-1']

    def assert_flow_all_users_from_comment_100(self, response: HttpResponse):
        """
        Assert that this scenario should result the same comments listed
        for all the users (AnonymousUser, ValidUser, StaffUser,
        SuperUser, SuperStaffUser).
        """
        parser = CommentsUpRecursiveParser(test=self, response=response)
        # Check comment ID 101
        comment_101 = parser.assert_and_return_commentid(comment_id=101)
        comment_101.assert_contains_content(
            content='comment ID 101 HTML content')
        comment_101.assert_time(value='2017-01-05T20:02:38.540040+00:00')
        comment_101.assert_vote_value(value=0)
        comment_101.assert_previous(
            comment_id=100, user_slug='banneduser', username='Banned&gt;User')
        comment_101.assert_no_replies()
        comment_101.assert_replies_order()
        # Check comment ID 100
        comment_100 = parser.assert_and_return_commentid(comment_id=100)
        comment_100.assert_contains_content(
            content='comment ID 100 HTML content')
        comment_100.assert_time(value='2017-01-05T20:01:38.540040+00:00')
        comment_100.assert_vote_value(value=0)
        comment_100.assert_no_previous()
        comment_100.assert_reply(
            comment_id=101, user_slug='inactiveuser', username='InactiveUser')
        comment_100.assert_replies_order()
        # Finish parsing
        parser.assert_same_topicgroup_tag(
            first=comment_101, second=comment_100)
        parser.assert_no_more_comments_and_order()

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
        self.assert_flow_all_users_from_comment_100(response=response)

    def test_shows_expansion_to_validuser_properly(self):
        """
        Should list the appropriate comment thread for `ValidUser`.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 100,
                'scroll_to_id': 100}))
        self.assert_flow_all_users_from_comment_100(response=response)

    def test_shows_expansion_to_staffuser_properly(self):
        """
        Should list the appropriate comment thread for `StaffUser`.
        """
        client = Client()
        client.login(username='StaffUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 100,
                'scroll_to_id': 100}))
        self.assert_flow_all_users_from_comment_100(response=response)

    def test_shows_expansion_to_superuser_properly(self):
        """
        Should list the appropriate comment thread for `SuperUser`.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 100,
                'scroll_to_id': 100}))
        self.assert_flow_all_users_from_comment_100(response=response)

    def test_shows_expansion_to_superstaffuser_properly(self):
        """
        Should list the appropriate comment thread for `SuperStaffUser`.
        """
        client = Client()
        client.login(username='SuperStaffUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 100,
                'scroll_to_id': 100}))
        self.assert_flow_all_users_from_comment_100(response=response)


class Scenario1Test2TestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with test scenario 1-2,
    testing expansion from comment 103.
    """

    fixtures = [
        'topic-tests-user',
        'comment-tests-topics-scenario-1',
        'comment-tests-comments-scenario-1']

    def assert_only_one_comment_visible(self, client: Client):
        """
        Assert what we created this scenario for: only one comment
        should be rendered for everyone.
        """
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-101',
                'comment_id': 103,
                'scroll_to_id': 103}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        # Check comment ID 101
        comment = parser.assert_and_return_commentid(comment_id=103)
        comment.assert_contains_content(content='comment ID 103 HTML content')
        comment.assert_time(value='2017-01-05T20:04:38.540040+00:00')
        comment.assert_vote_value(value=2)
        comment.assert_no_previous()
        comment.assert_no_replies()
        comment.assert_replies_order()
        # Finish parsing
        parser.assert_no_more_comments_and_order()

    def test_only_one_comment_visible(self):
        """
        Should expand only one comment in the thread since there are
        no more replies.
        """
        usertypes = [
            '', 'ValidUser', 'StaffUser', 'SuperUser', 'SuperStaffUser']
        for username in usertypes:
            client = Client()
            if username != '':
                client.login(username=username, password='ValidPassword')
            self.assert_only_one_comment_visible(client=client)


class Scenario1Test3TestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with test scenario 1-3,
    testing expansion from comment 104.
    """

    fixtures = [
        'topic-tests-user',
        'comment-tests-topics-scenario-1',
        'comment-tests-comments-scenario-1']

    def assert_same_for_everyone(self, client: Client):
        """
        Should render the right amount and the right format of comments
        for everyone.
        """
        client = Client()
        client.login(username='SuperUser', password='ValidPassword')
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-1-enabled-non-staff-topic-100',
                'comment_id': 104,
                'scroll_to_id': 104}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        # Check comment ID 107
        comment_107 = parser.assert_and_return_commentid(comment_id=107)
        comment_107.assert_user(
            user_slug='inactiveuser', username='InactiveUser')
        comment_107.assert_contains_content(
            content='comment ID 107 HTML content')
        comment_107.assert_time(value='2017-01-05T20:08:38.540040+00:00')
        comment_107.assert_vote_value(value=1)
        comment_107.assert_previous(
            comment_id=104, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_107.assert_no_replies()
        # Check comment ID 105
        comment_105 = parser.assert_and_return_commentid(comment_id=105)
        comment_105.assert_user(
            user_slug='banneduser', username='Banned&gt;User')
        comment_105.assert_contains_content(
            content='comment ID 105 HTML content')
        comment_105.assert_time(value='2017-01-05T20:06:38.540040+00:00')
        comment_105.assert_vote_value(value=1)
        comment_105.assert_previous(
            comment_id=104, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_105.assert_no_replies()
        # Check comment ID 104
        comment_104 = parser.assert_and_return_commentid(comment_id=104)
        comment_104.assert_user(
            user_slug='superstaffuser', username='SuperStaffUser')
        comment_104.assert_contains_content(
            content='comment ID 104 HTML content')
        comment_104.assert_time(value='2017-01-05T20:05:38.540040+00:00')
        comment_104.assert_vote_value(value=0)
        comment_104.assert_no_previous()
        comment_104.assert_reply(
            comment_id=107, user_slug='inactiveuser', username='InactiveUser')
        comment_104.assert_reply(
            comment_id=105, user_slug='banneduser', username='Banned&gt;User')
        comment_104.assert_replies_order()
        # Check if comments belong to the expected topic group Tag
        parser.assert_same_topicgroup_tag(
            first=comment_105, second=comment_104)
        parser.assert_different_topicgroup(
            first=comment_107, second=comment_104)
        # Finish parsing
        parser.assert_no_more_comments_and_order()

    def test_renders_properly_for_everyone(self):
        """
        Should render the same thread and the same format of comments
        for everyone in this scenario.
        """
        usertypes = [
            '', 'ValidUser', 'StaffUser', 'SuperUser', 'SuperStaffUser']
        for username in usertypes:
            client = Client()
            if username != '':
                client.login(username=username, password='ValidPassword')
            self.assert_same_for_everyone(client=client)


class Scenario2Test1TestCase(TestCase):
    """
    Testing `expand_comments_up_recursive` with test scenario 2-1,
    testing expansion from comment 200.
    """

    fixtures = [
        'topic-tests-user',
        'comment-tests-topics-scenario-2',
        'comment-tests-comments-scenario-2']

    def assert_visibility_for_non_admin(self, client: Client):
        """
        Non-admin (`AnonymousUser`, `ValidUser`) should not see staff
        topics in thread expansion.
        """
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-2-enabled-non-staff-topic-200',
                'comment_id': 200,
                'scroll_to_id': 200}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        # Check comment ID 201
        comment_201 = parser.assert_and_return_commentid(comment_id=201)
        comment_201.assert_user(
            user_slug='inactiveuser', username='InactiveUser')
        comment_201.assert_contains_content(
            content='comment ID 201 HTML content')
        comment_201.assert_time(value='2017-01-06T20:02:38.540040+00:00')
        comment_201.assert_vote_value(value=0)
        comment_201.assert_previous(
            comment_id=200, user_slug='banneduser',
            username='Banned&gt;User')
        comment_201.assert_no_replies()
        # Check comment ID 200
        comment_200 = parser.assert_and_return_commentid(comment_id=200)
        comment_200.assert_user(
            user_slug='banneduser', username='Banned&gt;User')
        comment_200.assert_contains_content(
            content='comment ID 200 HTML content')
        comment_200.assert_time(value='2017-01-06T20:01:38.540040+00:00')
        comment_200.assert_vote_value(value=0)
        comment_200.assert_no_previous()
        comment_200.assert_reply(
            comment_id=201, user_slug='inactiveuser', username='InactiveUser')
        comment_200.assert_replies_order()
        # Finishing parser assertions
        parser.assert_same_topicgroup_tag(
            first=comment_201, second=comment_200)
        parser.assert_no_more_comments_and_order()

    def assert_visibility_for_admin(self, client: Client):
        """
        Admin (`StaffUser`, `SuperUser`, `SuperStaffUser`) should see
        staff topics in thread expansion.
        """
        response = client.get(reverse(
            viewname='forum:base:comments-up-recursive', kwargs={
                'topic_slug': 'scenario-2-enabled-non-staff-topic-200',
                'comment_id': 200,
                'scroll_to_id': 200}))
        parser = CommentsUpRecursiveParser(test=self, response=response)
        # Check comment ID 207
        comment_207 = parser.assert_and_return_commentid(comment_id=207)
        comment_207.assert_user(
            user_slug='inactiveuser', username='InactiveUser')
        comment_207.assert_previous(
            comment_id=204, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_207.assert_time(value='2017-01-06T20:08:38.540040+00:00')
        comment_207.assert_vote_value(value=1)
        comment_207.assert_contains_content(
            content='comment ID 207 HTML content')
        comment_207.assert_no_replies()
        # Check comment ID 206
        comment_206 = parser.assert_and_return_commentid(comment_id=206)
        comment_206.assert_user(user_slug='validuser', username='ValidUser')
        comment_206.assert_previous(
            comment_id=204, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_206.assert_time(value='2017-01-06T20:07:38.540040+00:00')
        comment_206.assert_vote_value(value=1)
        comment_206.assert_contains_content(
            content='comment ID 206 STAFF HTML content')
        comment_206.assert_no_replies()
        # Check comment ID 205
        comment_205 = parser.assert_and_return_commentid(comment_id=205)
        comment_205.assert_user(
            user_slug='banneduser', username='Banned&gt;User')
        comment_205.assert_previous(
            comment_id=204, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_205.assert_time(value='2017-01-06T20:06:38.540040+00:00')
        comment_205.assert_vote_value(value=1)
        comment_205.assert_contains_content(
            content='comment ID 205 HTML content')
        comment_205.assert_no_replies()
        # Check comment ID 204
        comment_204 = parser.assert_and_return_commentid(comment_id=204)
        comment_204.assert_user(
            user_slug='superstaffuser', username='SuperStaffUser')
        comment_204.assert_previous(
            comment_id=202, user_slug='staffuser',
            username='StaffUser')
        comment_204.assert_time(value='2017-01-06T20:05:38.540040+00:00')
        comment_204.assert_vote_value(value=0)
        comment_204.assert_contains_content(
            content='comment ID 204 HTML content')
        comment_204.assert_reply(
            comment_id=207, user_slug='inactiveuser', username='InactiveUser')
        comment_204.assert_reply(
            comment_id=206, user_slug='validuser', username='ValidUser')
        comment_204.assert_reply(
            comment_id=205, user_slug='banneduser', username='Banned&gt;User')
        comment_204.assert_replies_order()
        # Check comment ID 203
        comment_203 = parser.assert_and_return_commentid(comment_id=203)
        comment_203.assert_user(user_slug='superuser', username='SuperUser')
        comment_203.assert_previous(
            comment_id=202, user_slug='staffuser',
            username='StaffUser')
        comment_203.assert_time(value='2017-01-06T20:04:38.540040+00:00')
        comment_203.assert_vote_value(value=-3)
        comment_203.assert_contains_content(
            content='comment ID 203 HTML content')
        comment_203.assert_no_replies()
        # Check comment ID 202
        comment_202 = parser.assert_and_return_commentid(comment_id=202)
        comment_202.assert_user(user_slug='staffuser', username='StaffUser')
        comment_202.assert_previous(
            comment_id=200, user_slug='banneduser',
            username='Banned&gt;User')
        comment_202.assert_time(value='2017-01-06T20:03:38.540040+00:00')
        comment_202.assert_vote_value(value=0)
        comment_202.assert_contains_content(
            content='comment ID 202 STAFF HTML content')
        comment_202.assert_reply(
            comment_id=204, user_slug='superstaffuser',
            username='SuperStaffUser')
        comment_202.assert_reply(
            comment_id=203, user_slug='superuser', username='SuperUser')
        comment_202.assert_replies_order()
        # Check comment ID 201
        comment_201 = parser.assert_and_return_commentid(comment_id=201)
        comment_201.assert_user(
            user_slug='inactiveuser', username='InactiveUser')
        comment_201.assert_contains_content(
            content='comment ID 201 HTML content')
        comment_201.assert_time(value='2017-01-06T20:02:38.540040+00:00')
        comment_201.assert_vote_value(value=0)
        comment_201.assert_previous(
            comment_id=200, user_slug='banneduser',
            username='Banned&gt;User')
        comment_201.assert_no_replies()
        # Check comment ID 200
        comment_200 = parser.assert_and_return_commentid(comment_id=200)
        comment_200.assert_user(
            user_slug='banneduser', username='Banned&gt;User')
        comment_200.assert_contains_content(
            content='comment ID 200 HTML content')
        comment_200.assert_time(value='2017-01-06T20:01:38.540040+00:00')
        comment_200.assert_vote_value(value=0)
        comment_200.assert_no_previous()
        comment_200.assert_reply(
            comment_id=202, user_slug='staffuser', username='StaffUser')
        comment_200.assert_reply(
            comment_id=201, user_slug='inactiveuser', username='InactiveUser')
        comment_200.assert_replies_order()
        # Finishing parser assertions
        parser.assert_same_topicgroup_tag(
            first=comment_201, second=comment_200)
        parser.assert_different_topicgroup(
            first=comment_201, second=comment_202)
        parser.assert_different_topicgroup(
            first=comment_202, second=comment_203)
        parser.assert_different_topicgroup(
            first=comment_203, second=comment_204)
        parser.assert_same_topicgroup_tag(
            first=comment_204, second=comment_205)
        parser.assert_different_topicgroup(
            first=comment_205, second=comment_206)
        parser.assert_different_topicgroup(
            first=comment_206, second=comment_207)
        parser.assert_no_more_comments_and_order()

    def test_visibility_for_non_admin(self):
        """
        Test the thread visibility for non-admin users.
        """
        usertypes = ['', 'ValidUser']
        for username in usertypes:
            client = Client()
            if username != '':
                client.login(username=username, password='ValidPassword')
            self.assert_visibility_for_non_admin(client=client)

    def test_visibility_for_admin(self):
        """
        Test the thread visibility for non-admin users.
        """
        usertypes = ['StaffUser', 'SuperUser', 'SuperStaffUser']
        for username in usertypes:
            client = Client()
            if username != '':
                client.login(username=username, password='ValidPassword')
            self.assert_visibility_for_admin(client=client)
