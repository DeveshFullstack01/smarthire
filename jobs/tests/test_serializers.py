from django.contrib.auth import get_user_model
from django.test import TestCase

from jobs.models import Company, Job
from jobs.serializers import JobSerializer

User = get_user_model()


class JobSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="StrongPassword@123",
            role=User.Role.RECRUITER,
        )

        self.company = Company.objects.create(
            name="OpenAI Pvt Ltd",
            owner=self.user,
        )

        self.job = Job.objects.create(
            title="Java Backend Developer",
            description="Spring Boot Microservices",
            location="Bangalore",
            job_type=Job.JobType.FULL_TIME,
            salary=1500000,
            company=self.company,
        )

    def test_serializer_contains_expected_fields(self):
        serializer = JobSerializer(self.job)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "title",
                "description",
                "location",
                "job_type",
                "salary",
                "created_at",
            },
        )

    def test_serializer_data(self):
        serializer = JobSerializer(self.job)

        self.assertEqual(
            serializer.data["title"],
            "Java Backend Developer",
        )

        self.assertEqual(
            serializer.data["description"],
            "Spring Boot Microservices",
        )

        self.assertEqual(
            serializer.data["location"],
            "Bangalore",
        )

        self.assertEqual(
            serializer.data["job_type"],
            Job.JobType.FULL_TIME,
        )

    def test_serializer_valid_data(self):
        serializer = JobSerializer(
            data={
                "title": "Python Developer",
                "description": "Django REST Framework",
                "location": "Pune",
                "job_type": Job.JobType.PART_TIME,
                "salary": "1200000.00",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_serializer_missing_required_fields(self):
        serializer = JobSerializer(
            data={}
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "title",
            serializer.errors,
        )

        self.assertIn(
            "description",
            serializer.errors,
        )

        self.assertIn(
            "location",
            serializer.errors,
        )

        self.assertIn(
            "salary",
            serializer.errors,
        )

    def test_read_only_fields_are_ignored(self):
        serializer = JobSerializer(
            data={
                "id": 100,
                "created_at": "2026-01-01T10:00:00Z",
                "title": "React Developer",
                "description": "React + TypeScript",
                "location": "Remote",
                "job_type": Job.JobType.CONTRACT,
                "salary": "1800000.00",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "id",
            serializer.validated_data,
        )

        self.assertNotIn(
            "created_at",
            serializer.validated_data,
        )