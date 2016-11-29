from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.forms.fields import BooleanField, CharField
from django.forms.widgets import CheckboxInput, PasswordInput, TextInput
from django.utils.translation import ugettext_lazy as _


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

    is_permanent = BooleanField(
        label=_('Keep me logged in'),
        required=False,
        widget=CheckboxInput(
            attrs={
                'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        init_val = super(ForumAuthForm, self).__init__(*args, **kwargs)
        if kwargs.get('autofocus') is True:
            # Remove the autofocus for the main page
            self.fields['username'].widget.attrs['autofocus'] = ''
        return init_val
