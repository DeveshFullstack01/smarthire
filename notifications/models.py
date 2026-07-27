from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    A single in-app notification for one user.

    Always created through notifications.services.notify() rather than
    directly, so every notification in the system flows through one place.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    message = models.CharField(
        max_length=255,
    )

    url = models.CharField(
        max_length=255,
        blank=True,
        help_text="Where clicking the notification should take the user.",
    )

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["recipient", "is_read"],
                name="notif_recipient_read_idx",
            ),
        ]

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:40]}"
# Create your models here.