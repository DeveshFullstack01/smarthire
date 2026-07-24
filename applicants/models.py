from django.conf import settings
from django.db import models

from jobs.models import Job


class Application(models.Model):

    class Status(models.TextChoices):
        APPLIED = "Applied", "Applied"
        SCREENING = "Screening", "Screening"
        INTERVIEW = "Interview", "Interview"
        OFFER = "Offer", "Offer"
        REJECTED = "Rejected", "Rejected"

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
    )

    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-applied_at"]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "candidate",
                    "job",
                ],
                name="unique_candidate_job_application",
            )

        ]

    def __str__(self):
        return f"{self.candidate.username} -> {self.job.title}"