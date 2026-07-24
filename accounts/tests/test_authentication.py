from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.password = "StrongPassword@123"

        self.verified_user = User.objects.create_user(
            username="verifieduser",
            email="verified@example.com",
            password=self.password,
            is_verified=True,
        )

        self.unverified_user = User.objects.create_user(
            username="unverifieduser",
            email="unverified@example.com",
            password=self.password,
            is_verified=False,
        )

        self.login_url = reverse("login")

    def test_verified_user_can_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "verifieduser",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        self.assertEqual(
            response.data["user"]["username"],
            "verifieduser",
        )

        self.assertEqual(
            response.data["user"]["email"],
            "verified@example.com",
        )

        self.assertEqual(
            response.data["user"]["role"],
            self.verified_user.role,
        )

    def test_unverified_user_cannot_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "unverifieduser",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertIn("detail", response.data)

        self.assertEqual(
            str(response.data["detail"]),
            "Please verify your email before logging in."
        )

    def test_invalid_password(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "verifieduser",
                "password": "WrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unknown_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "unknownuser",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )