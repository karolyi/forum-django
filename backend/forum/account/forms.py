from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms import ModelForm
from django.forms.fields import CharField
from django.forms.widgets import PasswordInput, TextInput
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

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        # Only list the ignored users in the SelectMultiple widget
        self.fields['ignored_users'].queryset = \
            self.instance.ignored_users.all()
