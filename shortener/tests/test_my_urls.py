from django.db import connection
from django.test.utils import CaptureQueriesContext
from unittest.mock import patch
from shortener.services.cache import RedisCacheService
from shortener.services.cache_keys import my_urls_cache_key
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from shortener.models import ShortURL
from shortener.services.cache import RedisCacheService
from shortener.services.cache_keys import my_urls_cache_key
from django.test import override_settings


class MyURLsTests(APITestCase):

    def setUp(self):

        self.cache = RedisCacheService()
        self.cache.client.flushdb()

        self.user = User.objects.create_user(
            username="myurlsuser",
            password="Password@123",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="Password@123",
        )

        self.user_url = ShortURL.objects.create(
            original_url="https://github.com",
            custom_alias="mygithub",
            owner=self.user,
        )

        self.other_url = ShortURL.objects.create(
            original_url="https://www.djangoproject.com",
            custom_alias="django",
            owner=self.other_user,
        )

        self.endpoint = "/api/my-urls/"

        def tearDown(self):
            self.cache.client.flushdb()

    def test_user_sees_only_own_urls(self):

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["custom_alias"],
            "mygithub",
        )

    def test_search_urls(self):

        self.client.force_authenticate(user=self.user)

        ShortURL.objects.create(
            original_url="https://www.python.org",
            custom_alias="python",
            owner=self.user,
        )

        response = self.client.get(
            self.endpoint,
            {"search": "python"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["custom_alias"],
            "python",
        )

    def test_order_urls_by_clicks(self):

        self.client.force_authenticate(user=self.user)

        ShortURL.objects.create(
            original_url="https://www.python.org",
            custom_alias="python",
            owner=self.user,
            clicks=10,
        )

        ShortURL.objects.create(
            original_url="https://www.djangoproject.com",
            custom_alias="django-user",
            owner=self.user,
            clicks=5,
        )

        response = self.client.get(
            self.endpoint,
            {"ordering": "-clicks"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            results[0]["custom_alias"],
            "python",
        )

        self.assertEqual(
            results[0]["clicks"],
            10,
        )

    def test_my_urls_pagination(self):

        self.client.force_authenticate(user=self.user)

        for i in range(5):
            ShortURL.objects.create(
                original_url=f"https://example{i}.com",
                custom_alias=f"example{i}",
                owner=self.user,
            )

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "count",
            response.data,
        )

        self.assertIn(
            "next",
            response.data,
        )

        self.assertIn(
            "previous",
            response.data,
        )

        self.assertIn(
            "results",
            response.data,
        )

    def test_my_urls_cache_is_created(self):

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.endpoint)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        cache = RedisCacheService()

        cache_key = my_urls_cache_key(
            self.user.id,
            "",
        )

        cached_data = cache.get(cache_key)

        self.assertIsNotNone(cached_data)

        self.assertEqual(
            cached_data["count"],
            1,
        )

        cache.delete(cache_key)

    @patch("shortener.api.my_urls.ShortURL.objects.filter")
    def test_my_urls_cache_hit(self, mock_filter):

        self.client.force_authenticate(user=self.user)

        # First request creates the cache.
        first_response = self.client.get(self.endpoint)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        mock_filter.reset_mock()

        # Second request should come from Redis.
        second_response = self.client.get(self.endpoint)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data,
            second_response.data,
        )

        mock_filter.assert_not_called()

        cache = RedisCacheService()

        cache.delete(
            my_urls_cache_key(
                self.user.id,
                "",
            )
        )

    def test_my_urls_cache_is_user_specific(self):

        self.client.force_authenticate(user=self.user)

        self.client.get(self.endpoint)

        self.client.force_authenticate(user=self.other_user)

        self.client.get(self.endpoint)

        cache = RedisCacheService()

        user_cache = cache.get(
            my_urls_cache_key(
                self.user.id,
                "",
            )
        )

        other_user_cache = cache.get(
            my_urls_cache_key(
                self.other_user.id,
                "",
            )
        )

        self.assertIsNotNone(user_cache)

        self.assertIsNotNone(other_user_cache)

        self.assertNotEqual(
            user_cache["results"][0]["custom_alias"],
            other_user_cache["results"][0]["custom_alias"],
        )

        cache.delete(
            my_urls_cache_key(
                self.user.id,
                "",
            )
        )

        cache.delete(
            my_urls_cache_key(
                self.other_user.id,
                "",
            )
        )

    def test_my_urls_cache_hit_avoids_database_query(self):

        self.client.force_authenticate(user=self.user)

        # First request populates Redis.
        first_response = self.client.get(self.endpoint)

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        # Second request should use Redis.
        with CaptureQueriesContext(connection) as queries:
            second_response = self.client.get(self.endpoint)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data,
            second_response.data,
        )

        self.assertEqual(
            len(queries),
            0,
        )
