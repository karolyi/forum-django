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

    def __init__(self, *args, **kwargs):
        is_autofocus = kwargs.pop('is_autofocus', False)
        init_val = super(ForumAuthForm, self).__init__(*args, **kwargs)
        if is_autofocus:
            # Remove the autofocus for the main page
            self.fields['username'].widget.attrs['autofocus'] = ''
        return init_val
