from django.core.urlresolvers import reverse
from django.test import Client, TestCase


class LogoutViewTest(TestCase):
    """
    Testing the logout view.
    """
    fixtures = ['users']

    def test_logs_out_and_redirects_user(self):
        """
        Should log out a logged-in user and redirect him to the his URL
        that's checked against ALLOWED_HOSTS.
        """
        client = Client(HTTP_REFERER='https://testhost/a/b/c/')
        client.login(username='ValidUser', password='ValidPassword')
        response = client.get(
            path=reverse(viewname='forum:account:logout'))
        self.assertRedirects(
            response=response, expected_url='/a/b/c/',
            fetch_redirect_response=False)
