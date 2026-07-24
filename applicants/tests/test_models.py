from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from applicants.models import Application
from jobs.models import Company, Job

User = get_user_model()


class ApplicationModelTests(TestCase):

    def setUp(self):
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

        self.company = Company.objects.create(
            name="OpenAI",
            owner=self.recruiter,
        )

        self.job = Job.objects.create(
            title="Java Backend Developer",
            description="Spring Boot",
            location="Bangalore",
            salary=1500000,
            company=self.company,
        )

    def test_create_application(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(
            application.candidate,
            self.candidate,
        )

        self.assertEqual(
            application.job,
            self.job,
        )

    def test_default_status(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertEqual(
            application.status,
            Application.Status.APPLIED,
        )

    def test_string_representation(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=Application.Status.INTERVIEW,
        )

        expected = (
            f"{self.candidate} -> "
            f"{self.job.title} "
            f"({Application.Status.INTERVIEW})"
        )

        self.assertEqual(
            str(application),
            expected,
        )

    def test_candidate_can_apply_only_once(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        with self.assertRaises(IntegrityError):
            Application.objects.create(
                candidate=self.candidate,
                job=self.job,
            )

    def test_delete_job_deletes_application(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.job.delete()

        self.assertEqual(
            Application.objects.count(),
            0,
        )

    def test_delete_candidate_deletes_application(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.candidate.delete()

        self.assertEqual(
            Application.objects.count(),
            0,
        )

    def test_match_score_can_be_null(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.assertIsNone(
            application.match_score,
        )

    def test_match_score_can_be_set(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            match_score=92.5,
        )

        self.assertEqual(
            application.match_score,
            92.5,
        )