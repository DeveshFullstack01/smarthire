def notifications(request):
    """
    Inject the current user's unread notifications into every template.

    Registered in settings.TEMPLATES so `unread_count` and
    `recent_notifications` are available on every page without each view
    having to provide them.
    """
    if not request.user.is_authenticated:
        return {
            "unread_count": 0,
            "recent_notifications": [],
        }

    qs = request.user.notifications.all()

    return {
        "unread_count": qs.filter(is_read=False).count(),
        "recent_notifications": qs[:5],
    }