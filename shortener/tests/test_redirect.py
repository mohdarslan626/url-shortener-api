from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from shortener.models import ShortURL
from datetime import timedelta
from django.utils import timezone

class RedirectTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="redirectuser",
            password="Password@123",
        )

        self.short_url = ShortURL.objects.create(
            original_url="https://github.com",
            short_code="test123",
            owner=self.user,
        )

        self.endpoint = "/test123/"

    def test_active_url_redirects(self):

        response = self.client.get(
            self.endpoint,
            follow=False,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            "https://github.com",
        )
        
    def test_redirect_increments_clicks(self):

        self.assertEqual(
            self.short_url.clicks,
            0,
        )

        response = self.client.get(
            self.endpoint,
            follow=False,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.short_url.refresh_from_db()

        self.assertEqual(
            self.short_url.clicks,
            1,
        )
        
    def test_disabled_url_returns_gone(self):

        self.short_url.is_active = False
        self.short_url.save(update_fields=["is_active"])

        response = self.client.get(
            self.endpoint,
            follow=False,
        )

        self.assertEqual(
            response.status_code,
            410,
        )

        self.assertEqual(
            response.content.decode(),
            "This URL has been disabled.",
        )
        
    def test_expired_url_returns_gone(self):

        self.short_url.expires_at = (
            timezone.now() - timedelta(days=1)
        )
        self.short_url.save(
            update_fields=["expires_at"]
        )

        response = self.client.get(
            self.endpoint,
            follow=False,
        )

        self.assertEqual(
            response.status_code,
            410,
        )

        self.assertEqual(
            response.content.decode(),
            "This URL has expired.",
        )