from django.db import models

from applicants.models import Application


class Interview(models.Model):

    class InterviewType(models.TextChoices):
        ONLINE = "Online", "Online"
        OFFLINE = "Offline", "Offline"
        PHONE = "Phone", "Phone"

    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        RESCHEDULED = "Rescheduled", "Rescheduled"

    class CandidateResponse(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        DECLINED = "Declined", "Declined"
        RESCHEDULE = "Reschedule", "Reschedule Requested"

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews",
    )

    interview_type = models.CharField(
        max_length=20,
        choices=InterviewType.choices,
        default=InterviewType.ONLINE,
    )

    scheduled_at = models.DateTimeField()

    duration_minutes = models.PositiveIntegerField(
        default=60,
    )

    meeting_link = models.URLField(
        blank=True,
    )

    interviewer_name = models.CharField(
        max_length=100,
    )

    notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    # ==============================
    # Candidate response (Phase 10)
    # ==============================

    candidate_response = models.CharField(
        max_length=20,
        choices=CandidateResponse.choices,
        default=CandidateResponse.PENDING,
    )

    candidate_note = models.TextField(
        blank=True,
        help_text="Candidate's reason when declining or requesting a reschedule.",
    )

    responded_at = models.DateTimeField(
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
        ordering = ["scheduled_at"]

    def __str__(self):
        return (
            f"{self.application.job.title} - "
            f"{self.application.candidate.username}"
        )