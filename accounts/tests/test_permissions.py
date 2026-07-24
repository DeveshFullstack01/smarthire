from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from accounts.permissions import (
    IsCandidate,
    IsRecruiter,
)

User = get_user_model()


class PermissionTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="StrongPassword@123",
            role=User.Role.RECRUITER,
        )

        self.candidate = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password="StrongPassword@123",
            role=User.Role.CANDIDATE,
        )

    def test_recruiter_permission_allows_recruiter(self):
        request = self.factory.get("/")
        request.user = self.recruiter

        permission = IsRecruiter()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_recruiter_permission_denies_candidate(self):
        request = self.factory.get("/")
        request.user = self.candidate

        permission = IsRecruiter()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_candidate_permission_allows_candidate(self):
        request = self.factory.get("/")
        request.user = self.candidate

        permission = IsCandidate()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_candidate_permission_denies_recruiter(self):
        request = self.factory.get("/")
        request.user = self.recruiter

        permission = IsCandidate()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_anonymous_user_denied_for_recruiter_permission(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        permission = IsRecruiter()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_anonymous_user_denied_for_candidate_permission(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        permission = IsCandidate()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )