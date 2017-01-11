from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms import ModelForm
from django.forms.fields import CharField
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _
from forum.base.models import Settings


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


class SettingsForm(ModelForm):
    class Meta:
        model = Settings
        fields = (
            'quote', 'comment_vote_hide_limit', 'introduction_md_all',
            'introduction_md_reg', 'introduction_md_friends',
            'uses_auto_bookmarks', 'mails_own_topic_comments',
            'mails_replies_topic', 'mails_moderation_topic', 'mails_messages',
            'separate_bookmarked_topics', 'show_outsiders', 'has_chat_enabled',
            'expand_archived')
