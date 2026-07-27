import logging

from .models import Notification

logger = logging.getLogger(__name__)


def notify(recipient, message, url=""):
    """
    Create one in-app notification for a user.

    This is the ONLY place notifications are created. Every feature that
    needs to notify someone calls this, so if we later add email, push,
    or batching, we change one function instead of hunting through views.

    Args:
        recipient: the User who should see the notification.
        message:   short one-line text (max 255 chars).
        url:       optional internal path to open on click, e.g. "/interviews/3/".

    Returns:
        The created Notification, or None if creation failed. A failure to
        notify must never crash the action that triggered it — scheduling
        an interview should still succeed even if the notification errors.
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

        return notification

    except Exception:
        logger.exception(
            "Failed to create notification. recipient_id=%s",
            getattr(recipient, "id", None),
        )
        return None
    
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