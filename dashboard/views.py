import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import User
from applicants.models import Application
from jobs.models import Job

logger = logging.getLogger(__name__)


@login_required
@role_required(User.Role.RECRUITER)
def recruiter_dashboard(request):
    logger.info(
        "Recruiter dashboard opened. recruiter_id=%s",
        request.user.id,
    )

    jobs = (
        Job.objects
        .filter(company__owner=request.user)
        .annotate(
            applicant_count=Count("applications")
        )
        .order_by("-created_at")
    )

    total_jobs = jobs.count()

    active_jobs = jobs.filter(
        status=Job.JobStatus.PUBLISHED
    ).count()

    closed_jobs = jobs.filter(
        status=Job.JobStatus.CLOSED
    ).count()

    applications = (
        Application.objects
        .filter(job__company__owner=request.user)
    )

    total_applicants = applications.count()

    interviews = applications.filter(
        status=Application.Status.INTERVIEW
    ).count()

    pending_applications = applications.filter(
        status=Application.Status.APPLIED
    ).count()

    average_match_score = (
        applications.aggregate(
            avg=Avg("match_score")
        )["avg"]
        or 0
    )

    recent_applications = (
        applications
        .select_related(
            "candidate",
            "job",
        )
        .order_by("-applied_at")[:5]
    )

    # --------------------------------------------
    # Applications by Status
    # --------------------------------------------

    application_status_data = (
        applications
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    application_status_labels = [
        item["status"]
        for item in application_status_data
    ]

    application_status_counts = [
        item["total"]
        for item in application_status_data
    ]

    # --------------------------------------------
    # Jobs by Status
    # --------------------------------------------

    job_status_data = (
        jobs
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    job_status_labels = [
        item["status"]
        for item in job_status_data
    ]

    job_status_counts = [
        item["total"]
        for item in job_status_data
    ]

    context = {
        "jobs": jobs[:5],
        "recent_applications": recent_applications,

        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "closed_jobs": closed_jobs,

        "total_applicants": total_applicants,
        "pending_applications": pending_applications,
        "interviews": interviews,

        "average_match_score": round(
            average_match_score,
            2,
        ),

        # Chart Data
        "application_status_labels": application_status_labels,
        "application_status_counts": application_status_counts,

        "job_status_labels": job_status_labels,
        "job_status_counts": job_status_counts,
    }

    return render(
        request,
        "dashboard/recruiter_dashboard.html",
        context,
    )