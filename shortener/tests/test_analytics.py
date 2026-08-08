from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from shortener.models import ShortURL


class AnalyticsTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="analyticsuser",
            password="Password@123",
        )

        self.short_url = ShortURL.objects.create(
            original_url="https://github.com",
            short_code="analytics1",
            custom_alias="gitstats",
            owner=self.user,
            clicks=5,
        )

        self.endpoint = "/api/analytics/gitstats/"

    def test_get_analytics(self):

        response = self.client.get(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["original_url"],
            "https://github.com",
        )

        self.assertEqual(
            response.data["short_code"],
            "analytics1",
        )

        self.assertEqual(
            response.data["custom_alias"],
            "gitstats",
        )

        self.assertEqual(
            response.data["clicks"],
            5,
        )
        
    def test_get_analytics_by_short_code(self):

        response = self.client.get(
            "/api/analytics/analytics1/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["short_code"],
            "analytics1",
        )

        self.assertEqual(
            response.data["clicks"],
            5,
        )
        
    def test_get_analytics_with_invalid_code(self):

        response = self.client.get(
            "/api/analytics/doesnotexist/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )