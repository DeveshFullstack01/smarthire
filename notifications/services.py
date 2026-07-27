import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


def notify(recipient, message, url="", email_subject=None):
    """
    Create one in-app notification for a user, and optionally email them.

    This is the ONLY place notifications are created, so every channel
    (in-app now, email here, push later) lives in one function.

    Args:
        recipient:     the User to notify.
        message:       short one-line text (max 255 chars).
        url:           optional internal path to open on click.
        email_subject: if given, also send an email with this subject.
                       If None, no email is sent (in-app only).

    Returns:
        The created Notification, or None if the in-app row failed.
    """
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            message=message[:255],
            url=url,
        )
        logger.info(
            "Notification created. recipient_id=%s notification_id=%s",
            recipient.id,
            notification.id,
        )
    except Exception:
        logger.exception(
            "Failed to create notification. recipient_id=%s",
            getattr(recipient, "id", None),
        )
        return None

    # Email is a best-effort second channel. A mail failure must never
    # undo the in-app notification, so it gets its own try/except and we
    # still return the notification that was successfully created.
    if email_subject and getattr(recipient, "email", ""):
        _send_email(recipient, email_subject, message, url)

    return notification


def _send_email(recipient, subject, message, url):
    """Send a plain-text notification email. Swallows and logs failures."""
    body = message

    if url:
        body = f"{message}\n\n{settings.FRONTEND_URL}{url}"

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(
            "Notification email sent. recipient_id=%s",
            recipient.id,
        )
    except Exception:
        logger.exception(
            "Failed to send notification email. recipient_id=%s",
            recipient.id,
        )


def mark_all_read(user):
    """Mark every unread notification for this user as read. Returns the count."""
    updated = (
        user.notifications
        .filter(is_read=False)
        .update(is_read=True)
    )
    logger.info(
        "Marked notifications read. user_id=%s count=%s",
        user.id,
        updated,
    )
    return updated