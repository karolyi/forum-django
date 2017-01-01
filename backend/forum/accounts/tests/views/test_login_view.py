from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from ...views import LoginView

a = RequestFactory()


class LoginViewTestCase(TestCase):
    """
    Testing the Login view.
    """
    User = get_user_model()
    login_view = LoginView()
    factory = RequestFactory()

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
        response = client.get(reverse(viewname='forum:accounts:login'))
        self.assertEqual(response.status_code, 200)
