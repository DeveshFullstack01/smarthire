from django.db import models
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):

    class JobType(models.TextChoices):
        FULL_TIME = "Full Time", "Full Time"
        PART_TIME = "Part Time", "Part Time"
        INTERNSHIP = "Internship", "Internship"
        CONTRACT = "Contract", "Contract"

    class JobStatus(models.TextChoices):
        DRAFT = "Draft", "Draft"
        PUBLISHED = "Published", "Published"
        CLOSED = "Closed", "Closed"

    title = models.CharField(max_length=255)

    description = models.TextField()

    location = models.CharField(max_length=255)

    job_type = models.CharField(
        max_length=30,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    # ==============================
    # New Fields
    # ==============================

    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.DRAFT,
    )

    experience = models.PositiveIntegerField(
        default=0,
        help_text="Required experience in years",
    )

    vacancies = models.PositiveIntegerField(
        default=1,
    )

    application_deadline = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title