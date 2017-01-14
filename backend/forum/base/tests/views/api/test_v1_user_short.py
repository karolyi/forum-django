from unittest.mock import Mock, patch

from django.http.response import HttpResponseNotFound, JsonResponse
from django.test import Client, TestCase
from django.urls.base import reverse
from forum.rest_api.exceptions import NotProduceable


class V1UserShortTestCase(TestCase):
    """
    Testing `v1_user_short`.
    """
    fixtures = [
        'topic-tests-user', 'topic-tests-topic',
        'topic-tests-comments-staffonly', 'topic-tests-comments-normal',
        'topic-tests-comments-highlighted', 'topic-tests-comments-disabled',
        'user-tests-rating']

    def setUp(self):
        """
        Test initialization code.
        """
        self.maxDiff = None

    @patch(
        'forum.base.views.api.cast_to_set_of_slug',
        side_effect=NotProduceable('stuff'))
    def test_fails_when_garbage_passed(self, mock_cast: Mock):
        """
        Should return a HTTP error when garbage is passed and the caster
        fails.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'foo'}))  # type: JsonResponse
        self.assertIs(type(response), JsonResponse)
        mock_cast.assert_called_once_with('foo')
        self.assertEqual(response.status_code, NotProduceable.status_code)

    def test_fails_for_invalid_usernames(self):
        """
        Should return HTTP 404 when the passed users aren't found.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'foo,bar'}))  # type: HttpResponseNotFound
        self.assertIs(type(response), HttpResponseNotFound)
        self.assertEqual(response.status_code, 404)

    def test_fails_for_partally_invalid_usernames(self):
        """
        Should return HTTP 404 when one of the passed users aren't
        found.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'validuser,bar'}))  # type: HttpResponseNotFound
        self.assertEqual(response.status_code, 404)

    def test_returns_one_user(self):
        """
        Should return a JSON with the one requested user information.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'validuser'}))  # type: JsonResponse
        self.assertIs(type(response), JsonResponse)
        self.assertDictEqual(response.json(), {
            'validuser': {
                'isBanned': False,
                'isStaff': False,
                'isSuperuser': False,
                'quote': 'validuser quote',
                'rating': {'avg': '2.50', 'count': 2}}})

    def test_shows_banned_status(self):
        """
        Should return a JSON with the one requested user information,
        showing that the user is banned.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'banneduser'}))  # type: JsonResponse
        self.assertIs(type(response), JsonResponse)
        self.assertDictEqual(response.json(), {
            'banneduser': {
                'isBanned': True,
                'isStaff': False,
                'isSuperuser': False,
                'quote': 'Banned>User quote',
                'rating': {'avg': 0, 'count': 0}}})

    def test_returns_two_users(self):
        """
        Should return a JSON with the two requested user information.
        """
        client = Client()
        response = client.get(reverse(
            viewname='forum:rest-api:v1-user-short', kwargs={
                'slug_list': 'validuser,superuser'}))  # type: JsonResponse
        self.assertIs(type(response), JsonResponse)
        self.assertDictEqual(response.json(), {
            'validuser': {
                'isBanned': False,
                'isStaff': False,
                'isSuperuser': False,
                'quote': 'validuser quote',
                'rating': {'avg': '2.50', 'count': 2}},
            'superuser': {
                'isBanned': False,
                'isStaff': False,
                'isSuperuser': True,
                'quote': 'superuser quote',
                'rating': {'avg': '0.00', 'count': 3}}})
