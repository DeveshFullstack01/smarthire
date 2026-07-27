"""Aggregates the data shown on the candidate dashboard."""

from applicants.models import Application
from interviews.models import Interview

from .profile_services import get_or_create_profile


def get_candidate_dashboard_data(user):
    """Return all stats and recent items for a candidate's dashboard."""
    applications = (
        Application.objects
        .filter(candidate=user)
        .select_related("job", "job__company")
    )

    interviews = (
        Interview.objects
        .filter(application__candidate=user)
        .select_related("application__job")
    )

    profile = get_or_create_profile(user)

    # Count applications by status in one pass over already-fetched rows,
    # avoiding a separate query per status.
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    return {
        "total_applications": len(applications),
        "in_progress": sum(
            status_counts.get(s, 0)
            for s in (
                Application.Status.SCREENING,
                Application.Status.INTERVIEW,
                Application.Status.OFFER,
            )
        ),
        "offers": status_counts.get(Application.Status.OFFER, 0),
        "rejected": status_counts.get(Application.Status.REJECTED, 0),
        "total_interviews": len(interviews),
        "upcoming_interviews": [
            iv for iv in interviews
            if iv.status == Interview.Status.SCHEDULED
        ][:5],
        "recent_applications": list(
            applications.order_by("-applied_at")[:5]
        ),
        "profile_completion": profile.completion_percentage,
        "status_labels": [s.label for s in Application.Status],
        "status_data": [
            status_counts.get(s.value, 0) for s in Application.Status
        ],
    }