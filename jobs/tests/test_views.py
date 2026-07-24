from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import Company, Job

User = get_user_model()


class JobCreateViewTests(APITestCase):

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
            name="OpenAI Pvt Ltd",
            owner=self.recruiter,
        )

        self.candidate = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password=self.password,
            role=User.Role.CANDIDATE,
            is_verified=True,
        )

        self.url = reverse("api-job-create")

    def test_recruiter_can_create_job(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.post(
            self.url,
            {
                "title": "Java Backend Developer",
                "description": "Spring Boot Microservices",
                "location": "Bangalore",
                "job_type": Job.JobType.FULL_TIME,
                "salary": "1500000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Job.objects.count(),
            1,
        )

        job = Job.objects.first()

        self.assertEqual(
            job.company,
            self.company,
        )

        self.assertEqual(
            job.title,
            "Java Backend Developer",
        )

    def test_candidate_cannot_create_job(self):
        self.client.force_authenticate(user=self.candidate)

        response = self.client.post(
            self.url,
            {
                "title": "Java Developer",
                "description": "Spring Boot",
                "location": "Delhi",
                "job_type": Job.JobType.FULL_TIME,
                "salary": "1200000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Job.objects.count(),
            0,
        )

    def test_unauthenticated_user_cannot_create_job(self):
        response = self.client.post(
            self.url,
            {
                "title": "Python Developer",
                "description": "Django",
                "location": "Remote",
                "job_type": Job.JobType.FULL_TIME,
                "salary": "1000000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_invalid_request_returns_400(self):
        self.client.force_authenticate(user=self.recruiter)

        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_recruiter_without_company_cannot_create_job(self):
        recruiter = User.objects.create_user(
            username="recruiter2",
            email="recruiter2@example.com",
            password=self.password,
            role=User.Role.RECRUITER,
            is_verified=True,
        )

        self.client.force_authenticate(user=recruiter)

        response = self.client.post(
            self.url,
            {
                "title": "Backend Developer",
                "description": "Spring Boot",
                "location": "Mumbai",
                "job_type": Job.JobType.FULL_TIME,
                "salary": "1000000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Job.objects.count(),
            0,
        )