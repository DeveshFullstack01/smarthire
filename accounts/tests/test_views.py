from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tokens import email_verification_token

User = get_user_model()


class CandidateSignupViewTests(APITestCase):

    @patch("accounts.views.send_verification_email")
    def test_candidate_signup_success(self, mock_send_email):
        response = self.client.post(
            reverse("candidate-signup"),
            {
                "username": "candidate1",
                "email": "candidate@example.com",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            User.objects.filter(
                username="candidate1"
            ).exists()
        )

        mock_send_email.assert_called_once()

    def test_candidate_signup_duplicate_username(self):
        User.objects.create_user(
            username="candidate1",
            email="existing@example.com",
            password="StrongPassword@123",
        )

        response = self.client.post(
            reverse("candidate-signup"),
            {
                "username": "candidate1",
                "email": "new@example.com",
                "password": "StrongPassword@123",
            },
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


class RecruiterSignupViewTests(APITestCase):

    @patch("accounts.views.send_verification_email")
    def test_recruiter_signup_success(self, mock_send_email):
        response = self.client.post(
            reverse("recruiter-signup"),
            {
                "username": "recruiter1",
                "email": "recruiter@example.com",
                "password": "StrongPassword@123",
                "company_name": "OpenAI Pvt Ltd",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            User.objects.filter(
                username="recruiter1"
            ).exists()
        )

        mock_send_email.assert_called_once()


class VerifyEmailViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="verifyuser",
            email="verify@example.com",
            password="StrongPassword@123",
            is_verified=False,
        )

    def test_verify_email_success(self):
        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        token = email_verification_token.make_token(
            self.user
        )

        response = self.client.get(
            reverse(
                "verify-email",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.is_verified
        )

    def test_verify_email_invalid_token(self):
        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        response = self.client.get(
            reverse(
                "verify-email",
                kwargs={
                    "uidb64": uid,
                    "token": "invalid-token",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class ResendVerificationViewTests(APITestCase):

    @patch("accounts.views.send_verification_email")
    def test_resend_verification_success(self, mock_send_email):
        User.objects.create_user(
            username="candidate2",
            email="candidate2@example.com",
            password="StrongPassword@123",
            is_verified=False,
        )

        response = self.client.post(
            reverse("resend-verification"),
            {
                "email": "candidate2@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        mock_send_email.assert_called_once()

    def test_resend_verification_user_not_found(self):
        response = self.client.post(
            reverse("resend-verification"),
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @patch("accounts.views.send_verification_email")
    def test_resend_verification_already_verified(
        self,
        mock_send_email,
    ):
        User.objects.create_user(
            username="verified",
            email="verified@example.com",
            password="StrongPassword@123",
            is_verified=True,
        )

        response = self.client.post(
            reverse("resend-verification"),
            {
                "email": "verified@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        mock_send_email.assert_not_called()