from bs4.element import Tag
from django.http.response import HttpResponse
from django.test import Client, TestCase
from django.urls.base import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from forum.base.choices import COMMENT_VOTE_HIDE_CHOICES
from forum.base.models import IntroductionModification, User
from forum.testutils.html_result_parser import HtmlResultParserBase
from forum.testutils.render_form.simple import (
    CheckBoxInput, RenderFormSimpleParserBase, SelectInput, TextAreaInput,
    TextInput)

SETTINGS_PAGE_URL = reverse(viewname='forum:account:settings')

__doc__ = """
The tests in this file are end-to-end tests. The purpose is not to test
the forms or any functionality underlying the view, but to test them
as a whole, including the contracts between the functions.
"""

STR_COMMENT_HIDE_CHOICES = \
    [(str(x), str(y)) for x, y in COMMENT_VOTE_HIDE_CHOICES]


class SettingsFormTester(RenderFormSimpleParserBase):
    """
    A tester for the settings form.

    Field valued are not checked here, since that happens in the
    respective test case.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize and assert that the form elements are all rendered.
        """
        super(SettingsFormTester, self).__init__(*args, **kwargs)
        # Assert the rendering of one single select menu
        self.assert_comment_hide_limit()
        # Assert the rendering of one multiple select menu
        self.assert_ignored_users()
        # And another multiple select but less assertion (speedup)
        self.assert_friended_users()
        # Assert one checkbox to see the rendering works properly
        self.assert_uses_auto_bookmarks()
        # And get the rest without extensive checking
        self.mails_own_topic_comments = CheckBoxInput(
            test=self.test, soup=self.soup, name='mails_own_topic_comments')
        self.mails_replies_topic = CheckBoxInput(
            test=self.test, soup=self.soup, name='mails_replies_topic')
        self.has_chat_enabled = CheckBoxInput(
            test=self.test, soup=self.soup, name='has_chat_enabled')
        self.mails_moderation_topic = CheckBoxInput(
            test=self.test, soup=self.soup, name='mails_moderation_topic')
        self.separate_bookmarked_topics = CheckBoxInput(
            test=self.test, soup=self.soup, name='separate_bookmarked_topics')
        self.expand_archived = CheckBoxInput(
            test=self.test, soup=self.soup, name='expand_archived')
        self.mails_messages = CheckBoxInput(
            test=self.test, soup=self.soup, name='mails_messages')
        self.assert_no_more_widgets(widgets=[
            self.comment_vote_hide_limit, self.ignored_users,
            self.friended_users, self.uses_auto_bookmarks,
            self.mails_own_topic_comments, self.mails_replies_topic,
            self.has_chat_enabled, self.mails_moderation_topic,
            self.separate_bookmarked_topics, self.expand_archived,
            self.mails_messages])

    def assert_comment_hide_limit(self):
        """
        Get and assert the vote hide limit select menu.
        """
        comment_hide = SelectInput(
            test=self.test, soup=self.soup, name='comment_vote_hide_limit')
        comment_hide.assert_rendered_options(
            option_list=STR_COMMENT_HIDE_CHOICES)
        comment_hide.assert_is_not_multiple()
        comment_hide.assert_label_content(text=force_text(
            s=User._meta.get_field('comment_vote_hide_limit').verbose_name))
        comment_hide.assert_help_text(text=force_text(
            s=User._meta.get_field('comment_vote_hide_limit').help_text))
        self.comment_vote_hide_limit = comment_hide

    def assert_ignored_users(self):
        """
        Assert that the ignored users select menu us rendered properly.
        """
        ignored_users = SelectInput(
            test=self.test, soup=self.soup, name='ignored_users')
        ignored_users.assert_is_multiple()
        ignored_users.assert_label_content(text=force_text(
            s=User._meta.get_field('ignored_users').verbose_name))
        ignored_users.assert_help_text(text=force_text(
            s=User._meta.get_field('ignored_users').help_text))
        self.ignored_users = ignored_users

    def assert_friended_users(self):
        """
        Assert and set the friended users property on the tester
        instance.
        """
        self.friended_users = SelectInput(
            test=self.test, soup=self.soup, name='friended_users')

    def assert_uses_auto_bookmarks(self):
        """
        Assert the existence of `uses_auto_bookmarks`, and check if that
        checkbox is rendered properly.
        """
        uses_auto_bookmarks = CheckBoxInput(
            test=self.test, soup=self.soup, name='uses_auto_bookmarks')
        uses_auto_bookmarks.assert_help_text(text=force_text(
            s=User._meta.get_field('uses_auto_bookmarks').help_text))
        uses_auto_bookmarks.assert_label_content(text=force_text(
            s=User._meta.get_field('uses_auto_bookmarks').verbose_name))
        self.uses_auto_bookmarks = uses_auto_bookmarks


class IntroModFormTester(RenderFormSimpleParserBase):
    """
    A tester for the introduction modification form.

    Field valued are not checked here, since that happens in the
    respective test case.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize and assert that the form elements are all rendered.
        """
        super(IntroModFormTester, self).__init__(*args, **kwargs)
        # Assert that the quote field is there and is rendered properly
        self.assert_quote()
        # Assert one textarea with all possible checks
        self.assert_introduction_md_all()
        # Get the remaining rendered fields
        self.introduction_md_friends = TextAreaInput(
            test=self.test, soup=self.soup, name='introduction_md_friends')
        self.introduction_md_reg = TextAreaInput(
            test=self.test, soup=self.soup, name='introduction_md_reg')
        # Finally, assert that no more widget has been rendered
        self.assert_no_more_widgets(widgets=[
            self.quote, self.introduction_md_all,
            self.introduction_md_friends, self.introduction_md_reg])

    def assert_introduction_md_all(self):
        """
        Assert that the `introduction_md_all` field is rendered
        properly, with all possible properties.
        """
        introduction_md_all = TextAreaInput(
            test=self.test, soup=self.soup, name='introduction_md_all')
        introduction_md_all.assert_help_text(text=force_text(
            s=User._meta.get_field('introduction_md_all').help_text))
        introduction_md_all.assert_label_content(text=force_text(
            s=User._meta.get_field('introduction_md_all').verbose_name))
        self.introduction_md_all = introduction_md_all

    def assert_quote(self):
        """
        Assert that the quote is there and has the expected properties.
        """
        quote = TextInput(test=self.test, soup=self.soup, name='quote')
        quote.assert_help_text(text=force_text(
            s=User._meta.get_field('quote').help_text))
        quote.assert_label_content(text=force_text(
            s=User._meta.get_field('quote').verbose_name))
        self.quote = quote


class SettingsPageParser(HtmlResultParserBase):
    """
    HTML Parser for the settings page.
    """

    def __init__(self, test: TestCase, response: HttpResponse):
        super(SettingsPageParser, self).__init__(test=test, response=response)
        self.form = self.soup.find(name='form', class_='settings-form')
        self.test.assertIsInstance(obj=self.form, cls=Tag)
        self.assert_has_csrf()
        self.assert_has_submit()
        self.settings_form = SettingsFormTester(
            soup=self.soup, class_='form-part-settings', test=self.test)
        self.intro_form = IntroModFormTester(
            soup=self.soup, class_='form-part-intro-mod', test=self.test)

    def assert_has_csrf(self):
        """
        Assert that the form has a CSRF tag that's hidden.
        """
        csrf = self.form.find(name='input', attrs={
            'type': 'hidden', 'name': 'csrfmiddlewaretoken'})
        self.test.assertIsInstance(obj=csrf, cls=Tag, msg=_(
            'Expected a CSRF tag in the form but none found.'))

    def assert_has_message(self, extra_tags: str, level: str=None):
        """
        Assert that a message within the form is rendered with the
        passed ID tag (that is a class name added).
        """
        message = self.form.find(name='div', class_=extra_tags)  # type: Tag
        self.test.assertIsInstance(obj=message, cls=Tag, msg=_(
            'Expected to find a message with extra tags {extra_tags} but '
            'found none.').format(extra_tags=extra_tags))
        if level is not None:
            self.test.assertIn(
                member='alert-{level}'.format(level=level),
                container=message.attrs['class'], msg=_(
                    'Expected to find the message with the level {level} but '
                    'it doesn\'t have that class.').format(level=level))

    def assert_has_no_message(self, extra_tags: str):
        """
        Assert that a message within the form is rendered with the
        passed ID tag (that is a class name added).
        """
        message = self.form.find(name='div', class_=extra_tags)  # type: Tag
        if isinstance(message, Tag):
            self.test.fail(msg=_(
                'Expected NOT to found a message with tags {extra_tags} but '
                'found one.').format(extra_tags=extra_tags))

    def assert_has_submit(self):
        """
        Assert that the page has a submit button.
        """
        submit_tag = self.form.find(attrs={'type': 'submit'})
        self.test.assertIsInstance(obj=submit_tag, cls=Tag, msg=_(
            'Expected to find a submit element but found none.'))


class BasicTestCase(TestCase):
    """
    Testing the `SettingsView` with basic, simple tests.
    """

    fixtures = ['settings/settings-test-user.yaml']
    maxDiff = None

    def test_redirects_when_not_logged_in(self):
        """
        The settings view should be only available when the user is
        logged in.
        """
        client = Client()
        response = client.get(SETTINGS_PAGE_URL)
        expected_url = '{view}?next={settings_url}'.format(
            view=reverse(viewname='forum:account:login'),
            settings_url=SETTINGS_PAGE_URL)
        self.assertRedirects(response=response, expected_url=expected_url)

    def test_renders_form_with_validuser(self):
        """
        Should render the settings page when the user is logged in.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(SETTINGS_PAGE_URL)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.comment_vote_hide_limit.assert_one_selected(
            value='-5')
        parser.settings_form.ignored_users.assert_one_selected(
            value='superuser', content='SuperUser')
        parser.settings_form.friended_users.assert_multiple_selected(
            option_list=[
                ('archivesexpanderuser', 'ArchivesExpanderUser'),
                ('staffuser', 'StaffUser')])
        # Check once that the checkboxes show their states from DB
        parser.settings_form.uses_auto_bookmarks.assert_is_not_checked()
        parser.settings_form.mails_moderation_topic.assert_is_checked()
        parser.settings_form.mails_messages.assert_is_checked()
        parser.settings_form.separate_bookmarked_topics.assert_is_checked()
        parser.settings_form.has_chat_enabled.assert_is_checked()
        parser.settings_form.expand_archived.assert_is_not_checked()
        # A tricky quote that is already escaped but parsed back
        parser.intro_form.quote.assert_value(text='validuser <>" quote')
        parser.intro_form.introduction_md_all.assert_content(
            text='validuser md_all')
        parser.intro_form.introduction_md_reg.assert_content(
            text='validuser md_reg')
        parser.intro_form.introduction_md_friends.assert_content(
            text='validuser md_friends')

    def test_renders_form_with_archivesexpanderuser(self):
        """
        Assert that for another user (`ArchivesExpanderUser`) a
        different settings page state is rendered.
        """
        client = Client()
        client.login(username='ArchivesExpanderUser', password='ValidPassword')
        response = client.get(SETTINGS_PAGE_URL)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.comment_vote_hide_limit.assert_one_selected(
            value='-4')
        parser.settings_form.ignored_users.assert_none_selected()
        parser.settings_form.friended_users.assert_none_selected()
        parser.settings_form.uses_auto_bookmarks.assert_is_checked()
        parser.intro_form.quote.assert_value(text='ArchivesExpanderUser quote')
        # Can't escape the textarea
        parser.intro_form.introduction_md_all.assert_content(
            text='md_&lt;/textarea&gt;&lt;script language="text/javascript'
            '"&gt;alert("boop")&lt;/script&gt;all')
        parser.intro_form.introduction_md_reg.assert_content(text='md_reg')
        parser.intro_form.introduction_md_friends.assert_content(
            text='md_friends')

    def test_modifies_data_with_validuser(self):
        """
        Test that the user is able to post and gets the appropriate
        result.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.post(SETTINGS_PAGE_URL, data={
            'comment_vote_hide_limit': '-10',
            # Would change from ['superuser']
            'ignored_users': ['superstaffuser'],
            'friended_users': ['superuser'],
            'uses_auto_bookmarks': 'on',
            'quote': 'new ValidUser quote',
            'introduction_md_all': 'foo1',
            'introduction_md_reg': 'foo2',
            'introduction_md_friends': 'foo3',
        }, follow=True)
        self.assertRedirects(response=response, expected_url=SETTINGS_PAGE_URL)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.comment_vote_hide_limit.assert_one_selected(
            value='-10')
        parser.settings_form.ignored_users.assert_one_selected(
            value='superstaffuser')
        parser.settings_form.friended_users.assert_one_selected(
            value='superuser')
        parser.settings_form.ignored_users.assert_has_no_error()
        parser.settings_form.friended_users.assert_has_no_error()
        # No more elements should be rendered for the users
        parser.settings_form.ignored_users.assert_rendered_options(
            option_list=[('superstaffuser', 'SuperStaffUser')])
        parser.settings_form.friended_users.assert_rendered_options(
            option_list=[('superuser', 'SuperUser')])
        parser.settings_form.uses_auto_bookmarks.assert_is_checked()
        parser.intro_form.quote.assert_value(text='new ValidUser quote')
        parser.intro_form.introduction_md_all.assert_content(text='foo1')
        parser.intro_form.introduction_md_reg.assert_content(text='foo2')
        parser.intro_form.introduction_md_friends.assert_content(text='foo3')
        # Check that the model has been changed
        validuser = User.objects.get(slug='validuser')  # type: User
        # The quote should not have changed yet, nor the introductions
        self.assertEqual(validuser.quote, 'validuser <>" quote')
        self.assertEqual(validuser.introduction_md_all, 'validuser md_all')
        self.assertEqual(validuser.introduction_md_reg, 'validuser md_reg')
        self.assertEqual(
            validuser.introduction_md_friends, 'validuser md_friends')
        # The ignored and friended users should now have changed
        self.assertListEqual(
            list1=list(validuser.ignored_users.values_list('slug', flat=True)),
            list2=['superstaffuser'])
        self.assertListEqual(list1=list(
            validuser.friended_users.values_list('slug', flat=True)),
            list2=['superuser'])
        self.assertTrue(validuser.uses_auto_bookmarks)
        # Assert that an IntroductionModification model has been created
        intro_mod = IntroductionModification.objects.get(
            user=validuser)  # type: IntroductionModification
        self.assertEqual(intro_mod.quote, 'new ValidUser quote')
        self.assertEqual(intro_mod.introduction_md_all, 'foo1')
        self.assertEqual(intro_mod.introduction_md_reg, 'foo2')
        self.assertEqual(intro_mod.introduction_md_friends, 'foo3')
        # Assert the alerts in the HTML
        parser.assert_has_message(
            extra_tags='settings-is-saved', level='success')
        parser.assert_has_message(extra_tags='intro-saved-but-awaits-approval')
        parser.assert_has_message(extra_tags='intro-approval-is-waiting')

    def test_rejects_modification_when_settings_corrupt(self):
        """
        Should reject and not save the form when the user passed
        invalid data. Also, it should show error messages.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.post(SETTINGS_PAGE_URL, data={
            'comment_vote_hide_limit': '-5',
            # Would change from ['superuser']
            'ignored_users': ['banneduser', 'invalid-data-nouser'],
            # Removing selection
            'friended_users': [],
            'uses_auto_bookmarks': 'on',
            'quote': 'new ValidUser quote',
            'introduction_md_all': 'foo1',
            'introduction_md_reg': 'foo2',
            'introduction_md_friends': 'foo3',
        }, follow=True)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.ignored_users.assert_one_selected(
            value='banneduser', content='Banned&gt;User')
        parser.settings_form.friended_users.assert_none_selected()
        # No more elements should be rendered for the users
        parser.settings_form.ignored_users.assert_rendered_options(
            option_list=[('banneduser', 'Banned&gt;User')])
        parser.settings_form.friended_users.assert_rendered_options(
            option_list=[])
        parser.assert_has_no_message(extra_tags='settings-is-saved')
        parser.assert_has_no_message(
            extra_tags='intro-saved-but-awaits-approval')
        parser.assert_has_no_message(extra_tags='intro-approval-is-waiting')
        parser.assert_has_message(extra_tags='settings-not-saved')
        parser.settings_form.ignored_users.assert_has_error()
        parser.settings_form.friended_users.assert_has_no_error()
        # Regardless the error, the introduction should show the new
        # value
        parser.intro_form.introduction_md_all.assert_content(text='foo1')
        parser.intro_form.introduction_md_reg.assert_content(text='foo2')
        parser.settings_form.uses_auto_bookmarks.assert_is_checked()
        # Check that the model is unchanged
        validuser = User.objects.get(slug='validuser')  # type: User
        self.assertFalse(validuser.uses_auto_bookmarks)
        # Check that the user doesn't have an intro mod saved
        with self.assertRaises(
                expected_exception=IntroductionModification.DoesNotExist):
            IntroductionModification.objects.get(user=validuser)
        # The ignored users should be the original
        self.assertListEqual(
            list1=list(validuser.ignored_users.values_list('slug', flat=True)),
            list2=['superuser'])

    def test_cant_friend_or_ignore_self(self):
        """
        The form should reject the user trying to add himself as friend
        or ignored user.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.post(SETTINGS_PAGE_URL, data={
            # This is an invalid value here
            'comment_vote_hide_limit': '-5',
            'ignored_users': ['banneduser', 'validuser'],
            # Removing selection
            'friended_users': ['validuser'],
            'uses_auto_bookmarks': 'on',
            'quote': 'new ValidUser quote',
            'introduction_md_all': 'foo1',
            'introduction_md_reg': 'foo2',
            'introduction_md_friends': 'foo3',
        }, follow=True)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.ignored_users.assert_has_error()
        parser.settings_form.friended_users.assert_has_error()
        parser.settings_form.ignored_users.assert_rendered_options(
            option_list=[('banneduser', 'Banned&gt;User')])
        parser.settings_form.friended_users.assert_rendered_options(
            option_list=[])
        # The ignored users should be the original
        validuser = User.objects.get(slug='validuser')  # type: User
        self.assertListEqual(
            list1=list(validuser.ignored_users.values_list('slug', flat=True)),
            list2=['superuser'])
