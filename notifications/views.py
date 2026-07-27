import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import services
from .models import Notification

logger = logging.getLogger(__name__)


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()

    paginator = Paginator(notifications, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "notifications/notification_list.html",
        {
            "page_obj": page_obj,
            "notifications": page_obj.object_list,
        },
    )


@login_required
def open_notification(request, notification_id):
    """Mark one notification read, then redirect to wherever it points."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    return redirect(notification.url or "notification-list")


@login_required
@require_POST
def mark_all_read(request):
    services.mark_all_read(request.user)
    return redirect("notification-list")