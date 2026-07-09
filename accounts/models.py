from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        RECRUITER = "recruiter", "Recruiter"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
