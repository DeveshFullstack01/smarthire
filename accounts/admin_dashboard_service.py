"""Platform-wide analytics for the admin dashboard."""

from django.db.models import Count

from applicants.models import Application
from interviews.models import Interview
from jobs.models import Company, Job

from .models import User


def get_admin_dashboard_data():
    """Aggregate platform-wide counts and breakdowns for admins."""

    role_rows = (
        User.objects
        .values("role")
        .annotate(count=Count("id"))
    )
    role_counts = {row["role"]: row["count"] for row in role_rows}

    total_jobs = Job.objects.count()
    published_jobs = Job.objects.filter(
        status=Job.JobStatus.PUBLISHED
    ).count()

    status_rows = (
        Application.objects
        .values("status")
        .annotate(count=Count("id"))
    )
    status_map = {row["status"]: row["count"] for row in status_rows}

    return {
        "total_users": User.objects.count(),
        "total_candidates": role_counts.get(User.Role.CANDIDATE, 0),
        "total_recruiters": role_counts.get(User.Role.RECRUITER, 0),
        "total_admins": role_counts.get(User.Role.ADMIN, 0),
        "total_companies": Company.objects.count(),
        "total_jobs": total_jobs,
        "published_jobs": published_jobs,
        "total_applications": Application.objects.count(),
        "total_interviews": Interview.objects.count(),
        "unverified_users": User.objects.filter(is_verified=False).count(),
        "recent_users": list(
            User.objects.order_by("-date_joined")[:8]
        ),
        "recent_companies": list(
            Company.objects.select_related("owner").order_by("-id")[:5]
        ),
        "app_status_labels": [s.label for s in Application.Status],
        "app_status_data": [
            status_map.get(s.value, 0) for s in Application.Status
        ],
    }