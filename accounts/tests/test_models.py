from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):

    def test_default_role_is_candidate(self):
        user = User.objects.create_user(
            username="candidate1",
            email="candidate@example.com",
            password="StrongPassword@123",
        )

        self.assertEqual(
            user.role,
            User.Role.CANDIDATE,
        )

    def test_create_recruiter(self):
        user = User.objects.create_user(
            username="recruiter1",
            email="recruiter@example.com",
            password="StrongPassword@123",
            role=User.Role.RECRUITER,
        )

        self.assertEqual(
            user.role,
            User.Role.RECRUITER,
        )

    def test_create_admin(self):
        user = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="StrongPassword@123",
            role=User.Role.ADMIN,
        )

        self.assertEqual(
            user.role,
            User.Role.ADMIN,
        )

    def test_default_is_verified_false(self):
        user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPassword@123",
        )

        self.assertFalse(user.is_verified)

    def test_string_representation(self):
        user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPassword@123",
            role=User.Role.RECRUITER,
        )

        self.assertEqual(
            str(user),
            "john (recruiter)",
        )