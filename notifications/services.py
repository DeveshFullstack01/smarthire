import asyncio
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localtime

from .models import Notification

logger = logging.getLogger(__name__)


def notify(
    recipient,
    message,
    url="",
    email_subject=None,
):
    """
    Create an in-app notification,
    optionally send an email,
    and push a real-time WebSocket event.
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

    # ----------------------------
    # Email
    # ----------------------------

    if email_subject and recipient.email:
        _send_email(
            recipient,
            email_subject,
            message,
            url,
        )

    # ----------------------------
    # Live WebSocket Notification
    # ----------------------------

    _send_websocket_notification(notification)

    return notification


def _send_websocket_notification(notification):
    """
    Push a notification to every browser
    connected for this user.
    """

    try:
        channel_layer = get_channel_layer()

        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{notification.recipient.id}",
            {
                "type": "send_notification",
                "message": notification.message,
                "url": notification.url,
                "created_at": localtime(
                    notification.created_at
                ).strftime("%d %b %Y %I:%M %p"),
            },
        )

        logger.info(
            "Live notification sent. notification_id=%s",
            notification.id,
        )

    except Exception:
        logger.exception(
            "Failed to send live notification. notification_id=%s",
            notification.id,
        )


def _send_email(
    recipient,
    subject,
    message,
    url,
):
    """
    Send notification email.
    """

    body = message

    if url:
        body = (
            f"{message}\n\n"
            f"{settings.FRONTEND_URL}{url}"
        )

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
            "Failed to send email notification. recipient_id=%s",
            recipient.id,
        )


def mark_all_read(user):
    """
    Mark all notifications as read.
    """

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