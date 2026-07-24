from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from applicants.models import Application
from jobs.models import Company, Job

User = get_user_model()


class ApplicantViewsTests(TestCase):

    def setUp(self):
        self.password = "StrongPassword@123"

        self.recruiter = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password=self.password,
            role=User.Role.RECRUITER,
            is_verified=True,
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

        self.candidate = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password=self.password,
            role=User.Role.CANDIDATE,
            is_verified=True,
        )

    def test_candidate_can_apply_for_job(self):
        self.client.login(
            username="candidate",
            password=self.password,
        )

        response = self.client.get(
            reverse(
                "apply-job",
                args=[self.job.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("candidate-job-list"),
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )

    def test_duplicate_application_is_not_created(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.client.login(
            username="candidate",
            password=self.password,
        )

        response = self.client.get(
            reverse(
                "apply-job",
                args=[self.job.id],
            )
        )

        self.assertRedirects(
            response,
            reverse("candidate-job-list"),
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )

    def test_recruiter_can_update_status(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.client.login(
            username="recruiter",
            password=self.password,
        )

        response = self.client.post(
            reverse(
                "update-application-status",
                args=[application.id],
            ),
            {
                "status": Application.Status.SCREENING,
            },
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.SCREENING,
        )

        self.assertRedirects(
            response,
            reverse(
                "job-applicants",
                args=[self.job.id],
            ),
        )

    def test_invalid_transition_is_rejected(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            status=Application.Status.APPLIED,
        )

        self.client.login(
            username="recruiter",
            password=self.password,
        )

        response = self.client.post(
            reverse(
                "update-application-status",
                args=[application.id],
            ),
            {
                "status": Application.Status.OFFER,
            },
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.APPLIED,
        )

        self.assertRedirects(
            response,
            reverse(
                "update-application-status",
                args=[application.id],
            ),
        )

    def test_invalid_status_value(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.client.login(
            username="recruiter",
            password=self.password,
        )

        response = self.client.post(
            reverse(
                "update-application-status",
                args=[application.id],
            ),
            {
                "status": "INVALID",
            },
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.APPLIED,
        )

        self.assertRedirects(
            response,
            reverse(
                "update-application-status",
                args=[application.id],
            ),
        )

    def test_candidate_can_view_own_applications(self):
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.client.login(
            username="candidate",
            password=self.password,
        )

        response = self.client.get(
            reverse("my-applications")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Java Backend Developer",
        )

    def test_recruiter_cannot_access_candidate_page(self):
        self.client.login(
            username="recruiter",
            password=self.password,
        )

        response = self.client.get(
            reverse("my-applications")
        )

        self.assertNotEqual(
            response.status_code,
            200,
        )