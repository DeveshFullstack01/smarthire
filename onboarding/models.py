from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from offers.models import Offer


class EmployeeOnboarding(models.Model):

    # ==========================================
    # Onboarding Status
    # ==========================================

    class Status(models.TextChoices):
        NOT_STARTED = "Not Started", "Not Started"
        IN_PROGRESS = "In Progress", "In Progress"
        UNDER_REVIEW = "Under Review", "Under Review"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"
        COMPLETED = "Completed", "Completed"

    # ==========================================
    # Relationship
    # ==========================================

    offer = models.OneToOneField(
        Offer,
        on_delete=models.CASCADE,
        related_name="onboarding",
    )

    candidate = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_onboarding",
    )

    # ==========================================
    # Personal Information
    # ==========================================

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=20,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    # ==========================================
    # Address
    # ==========================================

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    pincode = models.CharField(
        max_length=10,
        blank=True,
    )

    # ==========================================
    # Emergency Contact
    # ==========================================

    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
    )

    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    # ==========================================
    # Government Identification
    # ==========================================

    pan_number = models.CharField(
        max_length=20,
        blank=True,
    )

    aadhaar_number = models.CharField(
        max_length=20,
        blank=True,
    )

    passport_number = models.CharField(
        max_length=30,
        blank=True,
    )

    driving_license_number = models.CharField(
        max_length=30,
        blank=True,
    )

    # ==========================================
    # Bank Details
    # ==========================================

    bank_name = models.CharField(
        max_length=150,
        blank=True,
    )

    account_number = models.CharField(
        max_length=50,
        blank=True,
    )

    ifsc_code = models.CharField(
        max_length=20,
        blank=True,
    )

    bank_branch = models.CharField(
        max_length=150,
        blank=True,
    )

    # ==========================================
    # Onboarding Status
    # ==========================================

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NOT_STARTED,
        db_index=True,
    )

    recruiter_note = models.TextField(
        blank=True,
    )

    candidate_note = models.TextField(
        blank=True,
    )

    rejection_reason = models.TextField(
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
            f"{self.candidate.username} - "
            f"{self.offer.designation}"
        )