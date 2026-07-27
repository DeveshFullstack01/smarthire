"""
Candidate profile models.

Kept in a separate module from the User model for readability, but still
part of the `accounts` app since they extend the user. Imported by
accounts/models.py so Django's autodetector picks them up.
"""

from django.conf import settings
from django.db import models


class CandidateProfile(models.Model):
    """One-to-one extension of a candidate User with profile details."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )

    headline = models.CharField(
        max_length=150,
        blank=True,
        help_text="e.g. 'Backend Developer | Django | PostgreSQL'",
    )

    bio = models.TextField(blank=True)

    phone = models.CharField(max_length=20, blank=True)

    location = models.CharField(max_length=120, blank=True)

    linkedin_url = models.URLField(blank=True)

    github_url = models.URLField(blank=True)

    portfolio_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

    @property
    def completion_percentage(self):
        """
        Rough profile-completion score out of 100.

        Weighted so that filling the core text fields plus adding at least
        one skill / experience / education entry approaches 100%.
        """
        checks = [
            bool(self.headline),
            bool(self.bio),
            bool(self.phone),
            bool(self.location),
            bool(self.linkedin_url or self.github_url or self.portfolio_url),
            self.skills.exists(),
            self.experiences.exists(),
            self.educations.exists(),
        ]
        earned = sum(1 for c in checks if c)
        return round(earned / len(checks) * 100)


class Skill(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="skills",
    )

    name = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "name"],
                name="unique_skill_per_profile",
            ),
        ]

    def __str__(self):
        return self.name


class Experience(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="experiences",
    )

    job_title = models.CharField(max_length=120)

    company = models.CharField(max_length=120)

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank if this is your current role.",
    )

    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.job_title} at {self.company}"

    @property
    def is_current(self):
        return self.end_date is None


class Education(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="educations",
    )

    degree = models.CharField(max_length=120)

    institution = models.CharField(max_length=150)

    start_year = models.PositiveIntegerField()

    end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-start_year"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"