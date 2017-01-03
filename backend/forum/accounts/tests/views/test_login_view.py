from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from ...views import LoginView


class LoginViewTestCase(TestCase):
    """
    Testing the Login view.
    """
    User = get_user_model()
    login_view = LoginView()
    factory = RequestFactory()
    fixtures = ['users']

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
        response = client.get(path=reverse(viewname='forum:accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_post_valid_active_user(self):
        """
        Should log the user in with valid credentials and active status.
        """
        client = Client()
        response = client.post(
            path=reverse(viewname='forum:accounts:login'),
            data={
                'username': 'ValidUser',
                'password': 'ValidPassword',
                'is_permanent': True},
            follow=False)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(
        #     response=response, expected_url=settings.LOGIN_REDIRECT_URL)
