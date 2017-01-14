from typing import Union

from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.forms.fields import CharField
from django.forms.widgets import PasswordInput, TextInput
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from forum.base.models import IntroductionModification, User


class ForumAuthForm(AuthenticationForm):
    """
    Extending `AuthenticationForm` with an is_permanent checkbox.
    """
    username = UsernameField(
        max_length=254,
        widget=TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Username')}))
    password = CharField(
        strip=False,
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Password')}))

    def __init__(self, *args, **kwargs):
        is_autofocus = kwargs.pop('is_autofocus', False)
        init_val = super(ForumAuthForm, self).__init__(*args, **kwargs)
        if is_autofocus:
            # Remove the autofocus for the main page
            self.fields['username'].widget.attrs['autofocus'] = ''
        return init_val


class IntroductionModificationForm(ModelForm):
    """
    A form that modifies the user's introductions, uses the
    :model:`forum_base.IntroductionModification`.

    After submitting this form, an admin has to approve.
    """

    class Meta:
        model = IntroductionModification
        exclude = ['user', 'images']

    @cached_property
    def last_intro_mod(self) -> Union[IntroductionModification, None]:
        """
        Return the :model:`forum_base.IntroductionModification` for the
        user.

        Return `None` if none exists.
        """
        try:
            return self._user.introductionmodification
        except IntroductionModification.DoesNotExist:
            return None

    def _get_initial_data(self):
        """
        If the user already has an enabled introduction/quote set, he
        must use that one that's enabled. If he has a modification
        that's not enabled yet, the form has to use that.
        """
        if self.last_intro_mod is None:
            # Return the user's already accepted introductions/quote
            return {
                'quote': self._user.quote,
                'introduction_md_all': self._user.introduction_md_all,
                'introduction_md_reg': self._user.introduction_md_reg,
                'introduction_md_friends': self._user.introduction_md_friends}
        # Otherwise return None since passing the instance does the same
        return None

    def __init__(self, *args, user: User, **kwargs):
        """
        Override the initial data here.
        """
        self._user = user
        kwargs['initial'] = self._get_initial_data()
        kwargs['instance'] = self.last_intro_mod
        return super(IntroductionModificationForm, self).__init__(
            *args, **kwargs)


class SettingsForm(ModelForm):
    """
    A settings form in which the user can modify every setting EXCEPT
    the introductions, because thosa are handled by the
    `IntroductionModificationForm`.
    """
    class Meta:
        model = User
        fields = [
            'comment_vote_hide_limit', 'ignored_users', 'friended_users',
            'uses_auto_bookmarks', 'mails_own_topic_comments',
            'mails_replies_topic', 'mails_moderation_topic', 'mails_messages',
            'separate_bookmarked_topics', 'has_chat_enabled',
            'expand_archived']

    def clean_ignored_users(self) -> QuerySet:
        ignored_users = self.cleaned_data['ignored_users']  # type: QuerySet
        if ignored_users.filter(slug=self.instance.slug).exists():
            raise ValidationError(
                message=_('Don\'t ignore yourself.'), code='invalid')
        return ignored_users

    def clean_friended_users(self):
        friended = self.cleaned_data['friended_users']  # type: QuerySet
        if friended.filter(slug=self.instance.slug).exists():
            raise ValidationError(
                message=_('No need to friend yourself.'), code='invalid')
        return friended

    def list_only_selected_fields(self):
        """
        At `HTTP GET`, only list the users that are selected, so we
        won't generate a lot of unnecessary HTML. Select2 will take care
        of loading the extra options available dynamically.
        """
        self.fields['ignored_users'].queryset = \
            self.instance.ignored_users.only('slug', 'username')
        self.fields['friended_users'].queryset = \
            self.instance.friended_users.only('slug', 'username')

    def __init__(self, *args, **kwargs):
        return_value = super(SettingsForm, self).__init__(*args, **kwargs)
        if not self.data:
            # data = {}, HTTP GET time
            self.list_only_selected_fields()
        return return_value
