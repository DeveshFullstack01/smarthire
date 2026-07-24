from django.contrib.auth import get_user_model
from django.test import TestCase

from jobs.models import Company, Job

User = get_user_model()


class CompanyModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="StrongPassword@123",
            role=User.Role.RECRUITER,
        )

    def test_create_company(self):
        company = Company.objects.create(
            name="OpenAI Pvt Ltd",
            owner=self.user,
        )

        self.assertEqual(
            company.name,
            "OpenAI Pvt Ltd",
        )

        self.assertEqual(
            company.owner,
            self.user,
        )

    def test_company_string_representation(self):
        company = Company.objects.create(
            name="Google India",
            owner=self.user,
        )

        self.assertEqual(
            str(company),
            "Google India",
        )


class JobModelTests(TestCase):

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

    def test_create_job(self):
        job = Job.objects.create(
            title="Java Backend Developer",
            description="Spring Boot Developer",
            location="Bangalore",
            job_type=Job.JobType.FULL_TIME,
            salary=1500000,
            company=self.company,
        )

        self.assertEqual(
            job.title,
            "Java Backend Developer",
        )

        self.assertEqual(
            job.company,
            self.company,
        )

        self.assertEqual(
            job.job_type,
            Job.JobType.FULL_TIME,
        )

    def test_default_job_type(self):
        job = Job.objects.create(
            title="Python Developer",
            description="Django Developer",
            location="Pune",
            salary=1200000,
            company=self.company,
        )

        self.assertEqual(
            job.job_type,
            Job.JobType.FULL_TIME,
        )

    def test_job_string_representation(self):
        job = Job.objects.create(
            title="React Developer",
            description="Frontend",
            location="Remote",
            salary=1000000,
            company=self.company,
        )

        self.assertEqual(
            str(job),
            "React Developer",
        )

    def test_company_has_jobs(self):
        Job.objects.create(
            title="Java Developer",
            description="Spring Boot",
            location="Delhi",
            salary=1400000,
            company=self.company,
        )

        Job.objects.create(
            title="Python Developer",
            description="Django",
            location="Mumbai",
            salary=1300000,
            company=self.company,
        )

        self.assertEqual(
            self.company.jobs.count(),
            2,
        )

    def test_delete_company_deletes_jobs(self):
        Job.objects.create(
            title="Java Developer",
            description="Spring Boot",
            location="Delhi",
            salary=1400000,
            company=self.company,
        )

        self.company.delete()

        self.assertEqual(
            Job.objects.count(),
            0,
        )