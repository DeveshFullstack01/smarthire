from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase

from applicants.models import Application
from jobs.models import Company, Job
from resumes.models import Resume

User = get_user_model()


class ResumeModelTests(TestCase):

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
            description="Spring Boot Developer",
            location="Bangalore",
            salary=1500000,
            company=self.company,
        )

        self.application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
        )

        self.resume_file = SimpleUploadedFile(
            "resume.pdf",
            b"Dummy PDF Content",
            content_type="application/pdf",
        )

    def test_create_resume(self):
        resume = Resume.objects.create(
            application=self.application,
            file=self.resume_file,
        )

        self.assertEqual(
            resume.application,
            self.application,
        )

    def test_string_representation(self):
        resume = Resume.objects.create(
            application=self.application,
            file=self.resume_file,
        )

        self.assertEqual(
            str(resume),
            f"Resume for {self.application}",
        )

    def test_parsed_data_can_be_null(self):
        resume = Resume.objects.create(
            application=self.application,
            file=self.resume_file,
        )

        self.assertIsNone(
            resume.parsed_data,
        )

    def test_parsed_data_can_be_saved(self):
        parsed = {
            "name": "John Doe",
            "skills": [
                "Java",
                "Spring Boot",
                "Docker",
            ],
        }

        resume = Resume.objects.create(
            application=self.application,
            file=self.resume_file,
            parsed_data=parsed,
        )

        self.assertEqual(
            resume.parsed_data,
            parsed,
        )

    def test_application_can_have_only_one_resume(self):
        Resume.objects.create(
            application=self.application,
            file=self.resume_file,
        )

        second_resume = SimpleUploadedFile(
            "resume2.pdf",
            b"Another PDF",
            content_type="application/pdf",
        )

        with self.assertRaises(IntegrityError):
            Resume.objects.create(
                application=self.application,
                file=second_resume,
            )

    def test_delete_application_deletes_resume(self):
        Resume.objects.create(
            application=self.application,
            file=self.resume_file,
        )

        self.application.delete()

        self.assertEqual(
            Resume.objects.count(),
            0,
        )