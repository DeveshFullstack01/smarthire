from django.db import models

from applicants.models import Application


class InterviewQuestion(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interview_questions",
    )

    skill = models.CharField(max_length=100)

    question = models.TextField()

    difficulty = models.CharField(
        max_length=20,
        default="Medium",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.skill} - {self.question[:40]}"
