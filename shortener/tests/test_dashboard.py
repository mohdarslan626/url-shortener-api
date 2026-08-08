from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from shortener.models import ShortURL


class DashboardTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboarduser",
            password="Password@123",
        )

        self.other_user = User.objects.create_user(
            username="dashboardother",
            password="Password@123",
        )

        self.endpoint = "/api/dashboard/"

    def create_url(
        self,
        owner,
        original_url,
        custom_alias,
        clicks=0,
        is_active=True,
        expires_at=None,
    ):
        return ShortURL.objects.create(
            owner=owner,
            original_url=original_url,
            custom_alias=custom_alias,
            clicks=clicks,
            is_active=is_active,
            expires_at=expires_at,
        )

    def test_dashboard_statistics(self):

        self.create_url(
            self.user,
            "https://github.com",
            "github",
            clicks=10,
        )

        self.create_url(
            self.user,
            "https://www.python.org",
            "python",
            clicks=5,
        )

        self.create_url(
            self.user,
            "https://example.com",
            "expired",
            clicks=2,
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.create_url(
            self.other_user,
            "https://other.com",
            "other",
            clicks=100,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        summary = response.data["summary"]

        self.assertEqual(
            summary["total_urls"],
            3,
        )

        self.assertEqual(
            summary["active_urls"],
            2,
        )

        self.assertEqual(
            summary["expired_urls"],
            1,
        )

        self.assertEqual(
            summary["total_clicks"],
            17,
        )

    def test_dashboard_most_clicked_url(self):

        self.create_url(
            self.user,
            "https://github.com",
            "github",
            clicks=25,
        )

        self.create_url(
            self.user,
            "https://python.org",
            "python",
            clicks=10,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        most_clicked = response.data["most_clicked_url"]

        self.assertEqual(
            most_clicked["short_code"],
            "github",
        )

        self.assertEqual(
            most_clicked["clicks"],
            25,
        )

    def test_dashboard_latest_url(self):

        first_url = self.create_url(
            self.user,
            "https://github.com",
            "github",
        )

        latest_url = self.create_url(
            self.user,
            "https://python.org",
            "python",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        recent_urls = response.data["recent_urls"]

        self.assertGreaterEqual(
            len(recent_urls),
            2,
        )

        self.assertEqual(
            recent_urls[0]["id"],
            latest_url.id,
        )

        self.assertNotEqual(
            recent_urls[0]["id"],
            first_url.id,
        )

    def test_dashboard_user_isolation(self):

        self.create_url(
            self.user,
            "https://github.com",
            "github",
            clicks=5,
        )

        self.create_url(
            self.other_user,
            "https://example.com",
            "other",
            clicks=100,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        summary = response.data["summary"]

        self.assertEqual(
            summary["total_urls"],
            1,
        )

        self.assertEqual(
            summary["total_clicks"],
            5,
        )

        self.assertEqual(
            response.data["most_clicked_url"]["short_code"],
            "github",
        )