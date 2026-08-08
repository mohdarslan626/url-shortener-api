from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from shortener.models import ShortURL


class UpdatePermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            password="Password@123",
        )

        self.other_user = User.objects.create_user(
            username="other",
            password="Password@123",
        )

        self.url = ShortURL.objects.create(
            original_url="https://github.com",
            owner=self.owner,
        )

        self.endpoint = f"/api/urls/{self.url.id}/"

    def test_owner_can_update_url(self):

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.patch(
            self.endpoint,
            {
                "original_url": "https://www.djangoproject.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.url.refresh_from_db()

        self.assertEqual(
            self.url.original_url,
            "https://www.djangoproject.com",
        )

    def test_other_user_cannot_update_url(self):

        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.patch(
            self.endpoint,
            {
                "original_url": "https://www.djangoproject.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

class DeletePermissionTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="deleteowner",
            password="Password@123",
        )

        self.other_user = User.objects.create_user(
            username="deleteother",
            password="Password@123",
        )

        self.url = ShortURL.objects.create(
            original_url="https://github.com",
            owner=self.owner,
        )

        self.endpoint = f"/api/urls/{self.url.id}/delete/"

    def test_owner_can_delete_url(self):

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.delete(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            ShortURL.objects.filter(
                id=self.url.id
            ).exists()
        )

    def test_other_user_cannot_delete_url(self):

        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.delete(
            self.endpoint
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            ShortURL.objects.filter(
                id=self.url.id
            ).exists()
        )