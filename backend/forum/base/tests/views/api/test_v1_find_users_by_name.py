from django.http.response import (
    HttpResponseNotAllowed, HttpResponseNotFound, JsonResponse)
from django.test import Client, TestCase
from django.urls.base import reverse

VIEW_URL = reverse(viewname='forum:rest-api:v1-find-users-by-name')


class V1FindUsersByNameTestCase(TestCase):
    """
    Testing `v1_find_users_by_name`.
    """

    fixtures = ['settings/v1-find-users-by-name']

    def setUp(self):
        """
        Get a new `Client` for each test.
        """
        self.client = Client()

    def test_refuses_http_post(self):
        """
        The view should only answer to `HTTP GET`.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.post(
            path=VIEW_URL, data={'name_contains': 'asd', 'page': '1'})
        self.assertIsInstance(obj=response, cls=HttpResponseNotAllowed)
        self.assertEqual(response.get('Allow'), 'GET')

    def test_refuses_anonymoususer(self):
        """
        The view should only serve logged-in users.
        """
        response = self.client.get(
            path=VIEW_URL, data={'name_contains': 'asd', 'page': '1'})
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_404_when_no_namecontains_passed(self):
        """
        Should return 404 when a `page_contains` parameter is not
        passed.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(path=VIEW_URL, data={'page': '1'})
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_404_when_short_namecontains_passed(self):
        """
        Should return 404 when a `page_contains` parameter is too short.
        """
        response = self.client.get(
            path=VIEW_URL, data={'name_contains': 'x', 'page': '1'})
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_404_when_pageid_is_garbage(self):
        """
        Should return 404 when a `page` parameter is not int compatible.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(
            path=VIEW_URL, data={'name_contains': 'xx', 'page': 'noint'})
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_users_but_self(self):
        """
        Should return a `JsonResponse` with all the matching users
        except the one requesting them.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(
            path=VIEW_URL, data={'name_contains': 'us'})  # type: JsonResponse
        self.assertIsInstance(obj=response, cls=JsonResponse)
        self.assertDictEqual(d1=response.json(), d2={
            'pagination': {'more': False},
            'results': [
                {'id': 'archivesexpanderuser', 'text': 'ArchivesExpanderUser'},
                {'id': 'banneduser', 'text': 'Banned>User'},
                {'id': 'inactiveuser', 'text': 'InactiveUser'},
                {'id': 'staffuser', 'text': 'StaffUser'},
                {'id': 'superstaffuser', 'text': 'SuperStaffUser'},
                {'id': 'superuser', 'text': 'SuperUser'}]})

    def test_returns_404_for_invalid_page_case_1(self):
        """
        Should return a `HttpResponseNotFound` because a nonexistent
        page ID was passed.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(
            path=VIEW_URL,
            data={'name_contains': 'us', 'page': '2'})  # type: JsonResponse
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_404_for_invalid_page_case_2(self):
        """
        Should return a `HttpResponseNotFound` because a wrong
        page ID was passed.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(
            path=VIEW_URL,
            data={'name_contains': 'us', 'page': '0'})  # type: JsonResponse
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)

    def test_returns_404_for_invalid_page_case_3(self):
        """
        Should return a `HttpResponseNotFound` because a wrong
        page ID was passed.
        """
        self.client.login(username='ValidUser', password='ValidPassword')
        response = self.client.get(
            path=VIEW_URL,
            data={'name_contains': 'us', 'page': '-1'})  # type: JsonResponse
        self.assertIsInstance(obj=response, cls=HttpResponseNotFound)
