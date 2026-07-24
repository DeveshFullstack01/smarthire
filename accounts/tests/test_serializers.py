from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.serializers import (
    CandidateSignupSerializer,
    RecruiterSignupSerializer,
)
from jobs.models import Company

User = get_user_model()


class CandidateSignupSerializerTests(TestCase):

    def test_create_candidate_successfully(self):
        serializer = CandidateSignupSerializer(
            data={
                "username": "candidate1",
                "email": "candidate@example.com",
                "password": "StrongPassword@123",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(user.username, "candidate1")
        self.assertEqual(user.email, "candidate@example.com")
        self.assertEqual(user.role, User.Role.CANDIDATE)
        self.assertTrue(
            user.check_password("StrongPassword@123")
        )

    def test_duplicate_username_validation(self):
        User.objects.create_user(
            username="candidate1",
            email="first@example.com",
            password="StrongPassword@123",
        )

        serializer = CandidateSignupSerializer(
            data={
                "username": "candidate1",
                "email": "second@example.com",
                "password": "StrongPassword@123",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "username",
            serializer.errors,
        )


class RecruiterSignupSerializerTests(TestCase):

    def test_create_recruiter_successfully(self):
        serializer = RecruiterSignupSerializer(
            data={
                "username": "recruiter1",
                "email": "recruiter@example.com",
                "password": "StrongPassword@123",
                "company_name": "OpenAI Pvt Ltd",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertEqual(
            user.role,
            User.Role.RECRUITER,
        )

        self.assertTrue(
            Company.objects.filter(
                owner=user,
                name="OpenAI Pvt Ltd",
            ).exists()
        )

    def test_password_is_hashed(self):
        serializer = RecruiterSignupSerializer(
            data={
                "username": "recruiter2",
                "email": "recruiter2@example.com",
                "password": "StrongPassword@123",
                "company_name": "Tech Corp",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertNotEqual(
            user.password,
            "StrongPassword@123",
        )

        self.assertTrue(
            user.check_password("StrongPassword@123")
        )