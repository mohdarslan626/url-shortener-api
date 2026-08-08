from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from shortener.models import ShortURL


class MyURLsTests(APITestCase):

    def setUp(self):
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

    def test_user_sees_only_own_urls(self):

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

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["custom_alias"],
            "mygithub",
        )
        
    def test_search_urls(self):

        self.client.force_authenticate(
            user=self.user
        )

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

        self.client.force_authenticate(
            user=self.user
        )

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

        self.client.force_authenticate(
            user=self.user
        )

        for i in range(5):
            ShortURL.objects.create(
                original_url=f"https://example{i}.com",
                custom_alias=f"example{i}",
                owner=self.user,
            )

        response = self.client.get(
            self.endpoint
        )

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
        