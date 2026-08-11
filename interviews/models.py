from django.db import models

from applicants.models import Application


class Interview(models.Model):

    # ==========================================
    # Interview Type
    # ==========================================

    class InterviewType(models.TextChoices):
        ONLINE = "Online", "Online"
        OFFLINE = "Offline", "Offline"
        PHONE = "Phone", "Phone"

    # ==========================================
    # Interview Round
    # ==========================================

    class InterviewRound(models.TextChoices):
        SCREENING = "Screening", "Screening"
        TECHNICAL_1 = "Technical 1", "Technical Round 1"
        TECHNICAL_2 = "Technical 2", "Technical Round 2"
        MANAGERIAL = "Managerial", "Managerial"
        HR = "HR", "HR"
        FINAL = "Final", "Final"

    # ==========================================
    # Interview Status
    # ==========================================

    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        RESCHEDULED = "Rescheduled", "Rescheduled"

    # ==========================================
    # Candidate Response
    # ==========================================

    class CandidateResponse(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        DECLINED = "Declined", "Declined"
        RESCHEDULE = "Reschedule", "Reschedule Requested"

    # ==========================================
    # Recruiter Recommendation
    # ==========================================

    class Recommendation(models.TextChoices):
        STRONG_HIRE = "Strong Hire", "Strong Hire"
        HIRE = "Hire", "Hire"
        HOLD = "Hold", "Hold"
        REJECT = "Reject", "Reject"

    # ==========================================
    # Relationships
    # ==========================================

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews",
    )

    # ==========================================
    # Interview Details
    # ==========================================

    interview_round = models.CharField(
        max_length=20,
        choices=InterviewRound.choices,
        default=InterviewRound.SCREENING,
        db_index=True,
    )

    interview_type = models.CharField(
        max_length=20,
        choices=InterviewType.choices,
        default=InterviewType.ONLINE,
        db_index=True,
    )

    scheduled_at = models.DateTimeField(
        db_index=True,
    )

    duration_minutes = models.PositiveIntegerField(
        default=60,
    )

    interviewer_name = models.CharField(
        max_length=100,
    )

    meeting_link = models.URLField(
        max_length=500,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )

    # ==========================================
    # Candidate Response
    # ==========================================

    candidate_response = models.CharField(
        max_length=20,
        choices=CandidateResponse.choices,
        default=CandidateResponse.PENDING,
    )

    candidate_note = models.TextField(
        blank=True,
        help_text="Candidate reason for declining or requesting reschedule.",
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ==========================================
    # Interview Evaluation
    # ==========================================

    technical_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Technical rating out of 5",
    )

    communication_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Communication rating out of 5",
    )

    problem_solving_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Problem Solving rating out of 5",
    )

    overall_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Overall interview rating",
    )

    recommendation = models.CharField(
        max_length=20,
        choices=Recommendation.choices,
        blank=True,
    )

    feedback = models.TextField(
        blank=True,
        help_text="Recruiter's interview feedback.",
    )

    # ==========================================
    # Audit Fields
    # ==========================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self):
        return (
            f"{self.application.job.title} | "
            f"{self.application.candidate.username} | "
            f"{self.interview_round}"
        )

    @property
    def average_rating(self):
        """
        Returns the average interview rating out of 5.
        """

        ratings = [
            self.technical_rating,
            self.communication_rating,
            self.problem_solving_rating,
        ]

        ratings = [rating for rating in ratings if rating is not None]

        if not ratings:
            return None

        return round(sum(ratings) / len(ratings), 2)