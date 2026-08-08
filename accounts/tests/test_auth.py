from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):

    def setUp(self):
        self.url = "/api/auth/register/"

    def test_register_user(self):

        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "Password@123",
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

        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):

        User.objects.create_user(
            username="newuser",
            email="newuser@test.com",
            password="Password@123",
        )

        data = {
            "username": "newuser",
            "email": "another@test.com",
            "password": "Password@123",
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
            "username",
            response.data,
        )

    def test_register_with_short_password(self):

        data = {
            "username": "shortpass",
            "email": "shortpass@test.com",
            "password": "1234567",
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
            "password",
            response.data,
        )


class LoginTests(APITestCase):

    def setUp(self):
        self.url = "/api/auth/login/"

        self.user = User.objects.create_user(
            username="loginuser",
            email="login@test.com",
            password="Password@123",
        )

    def test_login_with_valid_credentials(self):

        data = {
            "username": "loginuser",
            "password": "Password@123",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_login_with_invalid_credentials(self):

        data = {
            "username": "loginuser",
            "password": "WrongPassword123",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn(
            "access",
            response.data,
        )

        self.assertNotIn(
            "refresh",
            response.data,
        )
    
    def test_refresh_token(self):

        login_data = {
            "username": "loginuser",
            "password": "Password@123",
        }

        login_response = self.client.post(
            self.url,
            login_data,
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/auth/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )