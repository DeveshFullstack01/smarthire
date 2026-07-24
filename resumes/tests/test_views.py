from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from applicants.models import Application
from jobs.models import Company, Job
from resumes.models import Resume

User = get_user_model()


class ResumeViewTests(TestCase):

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
            description="Spring Boot Developer",
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

        self.application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.resume = SimpleUploadedFile(
            "resume.pdf",
            b"Dummy Resume Content",
            content_type="application/pdf",
        )

    @patch("resumes.views.calculate_match_score")
    def test_candidate_can_upload_resume(self, mock_match):
        mock_match.return_value = {
            "score": 91
        }

        self.client.login(
            username="candidate",
            password=self.password,
        )

        response = self.client.post(
            reverse(
                "upload-resume",
                args=[self.application.id],
            ),
            {
                "file": self.resume,
            },
        )

        self.assertRedirects(
            response,
            reverse("candidate-dashboard"),
        )

        self.assertEqual(
            Resume.objects.count(),
            1,
        )

        self.application.refresh_from_db()

        self.assertEqual(
            self.application.match_score,
            91,
        )

    @patch("resumes.views.calculate_match_score")
    def test_duplicate_resume_upload_is_prevented(self, mock_match):
        Resume.objects.create(
            application=self.application,
            file=self.resume,
        )

        self.client.login(
            username="candidate",
            password=self.password,
        )

        response = self.client.post(
            reverse(
                "upload-resume",
                args=[self.application.id],
            ),
            {
                "file": SimpleUploadedFile(
                    "resume2.pdf",
                    b"Another Resume",
                    content_type="application/pdf",
                )
            },
        )

        self.assertRedirects(
            response,
            reverse("candidate-dashboard"),
        )

        self.assertEqual(
            Resume.objects.count(),
            1,
        )

        mock_match.assert_not_called()

    def test_other_candidate_cannot_upload_resume(self):
        other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password=self.password,
            role=User.Role.CANDIDATE,
            is_verified=True,
        )

        self.client.login(
            username="other",
            password=self.password,
        )

        response = self.client.get(
            reverse(
                "upload-resume",
                args=[self.application.id],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_login_required(self):
        response = self.client.get(
            reverse(
                "upload-resume",
                args=[self.application.id],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )