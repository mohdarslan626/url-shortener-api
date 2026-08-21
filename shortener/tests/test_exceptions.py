from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase


class ExceptionHandlerTests(APITestCase):

    def test_validation_error_format(self):

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "",
                "password": "short",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertIn(
            "username",
            response.data,
        )

        self.assertIn(
            "password",
            response.data,
        )

    def test_not_found_error_format(self):

        response = self.client.get(
            "/api/analytics/nonexistent-code/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertIn(
            "error",
            response.data,
        )

        self.assertIn(
            "code",
            response.data["error"],
        )

        self.assertIn(
            "message",
            response.data["error"],
        )

    def test_permission_error_format(self):

        user = User.objects.create_user(
            username="exceptionuser",
            password="Password@123",
        )

        other_user = User.objects.create_user(
            username="otherexceptionuser",
            password="Password@123",
        )

        from shortener.models import ShortURL

        url = ShortURL.objects.create(
            original_url="https://github.com",
            owner=user,
        )

        self.client.force_authenticate(
            user=other_user
        )

        response = self.client.patch(
            f"/api/urls/{url.id}/",
            {
                "original_url": "https://python.org",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertIn(
            "error",
            response.data,
        )
