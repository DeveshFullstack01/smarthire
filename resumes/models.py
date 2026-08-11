from django.db import models

from applicants.models import Application


class Resume(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="resume",
    )

    file = models.FileField(
        upload_to="resumes/",
    )

    parsed_data = models.JSONField(
        blank=True,
        null=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return (
            f"{self.application.candidate.username} - "
            f"{self.application.job.title}"
        )