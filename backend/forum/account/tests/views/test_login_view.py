from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls.base import reverse
from forum.account.forms import ForumAuthForm

from ...views import LoginView


class LoginViewTestCase(TestCase):
    """
    Testing the Login view.
    """
    User = get_user_model()
    login_view = LoginView()
    factory = RequestFactory()
    fixtures = ['users']
    username_field = \
        User._meta.get_field(User.USERNAME_FIELD).verbose_name

    def test_get_redirects_if_already_authenticated(self):
        """
        The `GET` should redirect if the user is already authenticated.
        """
        request = self.factory.get('/bla/')
        request.user = self.User(username='x')
        response = self.login_view.get(request=request)
        response.client = Client()
        self.assertRedirects(
            response=response, expected_url=settings.LOGIN_REDIRECT_URL)

    def test_get_renders_html_if_not_authenticated(self):
        """
        The `GET` should render an HTML if the user is not authenticated.
        """
        client = Client()
        response = client.get(path=reverse(viewname='forum:account:login'))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_active_user(self):
        """
        Should log the user in with valid credentials and active status.
        """
        client = Client()
        response = client.post(
            path=reverse(viewname='forum:account:login'),
            data={
                'username': 'ValidUser',
                'password': 'ValidPassword',
                'is_permanent': True})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response, expected_url=settings.LOGIN_REDIRECT_URL)

    def test_post_invalid_active_user(self):
        """
        Should reject the user with invalid credentials and active status.
        """
        client = Client()
        response = client.post(
            path=reverse(viewname='forum:account:login'),
            data={
                'username': 'ValidUser',
                'password': 'inValidPassword',
                'is_permanent': True},
            follow=False)
        self.assertEqual(response.status_code, 200)
        markup = response.content.decode('utf-8')
        soup = BeautifulSoup(markup=markup, features='lxml')
        # Check if the global error display is there
        div_error = soup.select('main form.login-form div.global-error')
        str_error = ForumAuthForm.error_messages[
            'invalid_login'] % {'username': self.username_field}
        self.assertEqual(len(div_error), 1)
        self.assertIn(member=str_error, container=div_error[0].text)

    def test_post_valid_inactive_user(self):
        """
        Should reject the user in with valid credentials and inactive status.
        """
        client = Client()
        response = client.post(
            path=reverse(viewname='forum:account:login'),
            data={
                'username': 'InactiveUser',
                'password': 'ValidPassword',
                'is_permanent': True},
            follow=False)
        self.assertEqual(response.status_code, 200)
        markup = response.content.decode('utf-8')
        soup = BeautifulSoup(markup=markup, features='lxml')
        div_error = soup.select('main form.login-form div.global-error')
        # Check if the global error display is there
        self.assertEqual(len(div_error), 1)
        self.assertIn(
            member=str(ForumAuthForm.error_messages['inactive']),
            container=div_error[0].text)
