from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase


class ThrottlingTests(APITestCase):

    def setUp(self):
        cache.clear()

        self.endpoint = "/api/shorten/"

    def tearDown(self):
        cache.clear()

    def test_anonymous_user_is_throttled(self):

        for _ in range(20):
            response = self.client.post(
                self.endpoint,
                {
                    "original_url": "https://example.com",
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
            )

        response = self.client.post(
            self.endpoint,
            {
                "original_url": "https://example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    def test_authenticated_user_is_throttled(self):

        user = User.objects.create_user(
            username="throttleuser",
            password="Password@123",
        )

        self.client.force_authenticate(
            user=user
        )

        for _ in range(60):
            response = self.client.post(
                self.endpoint,
                {
                    "original_url": "https://example.com",
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
            )

        response = self.client.post(
            self.endpoint,
            {
                "original_url": "https://example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        