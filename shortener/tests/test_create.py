from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from shortener.models import ShortURL


User = get_user_model()


class CreateShortURLTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Password@123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.url = "/api/shorten/"

    def test_create_short_url(self):

        data = {
            "original_url": "https://github.com",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            ShortURL.objects.count(),
            1,
        )

        short_url = ShortURL.objects.first()

        self.assertEqual(
            short_url.original_url,
            "https://github.com",
        )

        self.assertEqual(
            short_url.owner,
            self.user,
        )

    def test_create_short_url_with_custom_alias(self):

        data = {
            "original_url": "https://github.com",
            "custom_alias": "GitHub",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        short_url = ShortURL.objects.first()

        self.assertEqual(
            short_url.custom_alias,
            "github",
        )

    def test_create_short_url_with_duplicate_alias(self):
        
        ShortURL.objects.create(
            original_url="https://github.com",
            custom_alias="github",
            owner=self.user,
        )

        data = {
            "original_url": "https://www.djangoproject.com",
            "custom_alias": "GitHub",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "custom_alias",
            response.data,
        )

    def test_create_short_url_with_reserved_alias(self):

        data = {
            "original_url": "https://github.com",
            "custom_alias": "admin",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "custom_alias",
            response.data,
        )

        self.assertEqual(
            response.data["custom_alias"][0],
            "This alias is reserved.",
        )

    def test_create_short_url_with_expired_date(self):

        expired_at = timezone.now() - timedelta(days=1)

        data = {
            "original_url": "https://github.com",
            "expires_at": expired_at.isoformat(),
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "expires_at",
            response.data,
        )

        self.assertEqual(
            response.data["expires_at"][0],
            "Expiry date must be in the future.",
        )

    def test_create_short_url_with_future_expiry(self):

        expires_at = timezone.now() + timedelta(days=7)

        data = {
            "original_url": "https://github.com",
            "expires_at": expires_at.isoformat(),
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        short_url = ShortURL.objects.first()

        self.assertEqual(
            short_url.expires_at,
            expires_at,
        )

    def test_create_short_url_without_authentication(self):
        
        self.client.force_authenticate(user=None)

        data = {
            "original_url": "https://github.com",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        short_url = ShortURL.objects.first()

        self.assertIsNone(
            short_url.owner,
        )