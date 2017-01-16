from bs4.element import Tag
from django.http.response import HttpResponse
from django.test import Client, TestCase
from django.urls.base import reverse
from django.utils.encoding import force_text
# from django.utils.translation import ugettext_lazy as _
from forum.base.choices import COMMENT_VOTE_HIDE_CHOICES
from forum.base.models import User
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
        self.settings_form = SettingsFormTester(
            soup=self.soup, class_='form-part-settings', test=self.test)
        self.intro_form = IntroModFormTester(
            soup=self.soup, class_='form-part-intro-mod', test=self.test)


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

    def test_renders_form_when_logged_in(self):
        """
        Should render the settings page when the user is logged in.
        """
        client = Client()
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(SETTINGS_PAGE_URL)
        parser = SettingsPageParser(test=self, response=response)
        parser.settings_form.comment_vote_hide_limit.assert_one_selected(
            value='-5')
