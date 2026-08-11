from django.db import models
from django.utils import timezone

from applicants.models import Application


class Offer(models.Model):

    # ==========================================
    # Offer Status
    # ==========================================

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"
        EXPIRED = "Expired", "Expired"
        WITHDRAWN = "Withdrawn", "Withdrawn"

    # ==========================================
    # Employment Type
    # ==========================================

    class EmploymentType(models.TextChoices):
        FULL_TIME = "Full Time", "Full Time"
        PART_TIME = "Part Time", "Part Time"
        CONTRACT = "Contract", "Contract"
        INTERN = "Intern", "Intern"

    # ==========================================
    # Relationships
    # ==========================================

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="offer",
    )

    # ==========================================
    # Offer Details
    # ==========================================

    designation = models.CharField(
        max_length=100,
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    work_location = models.CharField(
        max_length=150,
        default="",
        blank=True,
    )

    offered_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    joining_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    joining_date = models.DateField()

    expiry_date = models.DateField()

    offer_letter = models.FileField(
        upload_to="offer_letters/",
        blank=True,
        null=True,
    )

    # ==========================================
    # Candidate Response
    # ==========================================

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    recruiter_note = models.TextField(
        blank=True,
    )

    candidate_note = models.TextField(
        blank=True,
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True,
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
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.application.candidate.username} | "
            f"{self.designation} | "
            f"{self.status}"
        )

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def salary_in_lpa(self):
        """
        Returns salary in LPA.
        Example:
        1800000 -> 18.00
        """
        return round(float(self.offered_salary) / 100000, 2)

    @property
    def days_until_expiry(self):
        """
        Number of days remaining before offer expires.
        """
        return (self.expiry_date - timezone.now().date()).days