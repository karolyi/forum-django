from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, TestCase

from ...utils import get_next_url


class GetNextUrlTestCase(TestCase):
    """
    Testing `get_next_url`.
    """
    factory = RequestFactory()

    def test_returns_next_from_post(self):
        """
        Should return the URL in the `next` parameter, when passed from
        HTTP `POST`.
        """
        request = self.factory.post('/whatever/', {'next': '/bla/?a=b'})
        next_url = get_next_url(request)
        self.assertEqual(next_url, '/bla/?a=b')

    def test_returns_next_from_get(self):
        """
        Should return the URL in the `next` parameter, when passed from
        HTTP `GET`.
        """
        request = self.factory.get('/whatever/', {'next': '/bla/?a=b'})
        next_url = get_next_url(request)
        self.assertEqual(next_url, '/bla/?a=b')

    @patch.object(settings, 'ALLOWED_HOSTS', ['testhost'])
    def test_returns_referer(self):
        """
        Should return the referer if valid.
        """
        request = self.factory.post(
            '/whatever/', HTTP_REFERER='http://testhost/x/y/?a=b')
        next_url = get_next_url(request)
        self.assertEqual(next_url, '/x/y/?a=b')

    def test_no_next_no_referrer(self):
        """
        Should return the referer if valid.
        """
        request = self.factory.post('/whatever/')
        next_url = get_next_url(request)
        self.assertEqual(next_url, settings.LOGIN_REDIRECT_URL)

    @patch.object(settings, 'ALLOWED_HOSTS', ['valid_host'])
    def test_invalid_referrer(self):
        """
        Should return the referer if valid.
        """
        request = self.factory.post(
            '/whatever/', HTTP_REFERER='http://invalid_host/x/y/?a=b')
        next_url = get_next_url(request)
        self.assertEqual(next_url, settings.LOGIN_REDIRECT_URL)
