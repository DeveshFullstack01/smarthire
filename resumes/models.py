from django.db import models
from applicants.models import Application


class Resume(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="resume",
    )
    file = models.FileField(upload_to="resumes/")
    parsed_data = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume for {self.application}"