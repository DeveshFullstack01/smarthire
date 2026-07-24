import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from jobs.models import Job

from .models import Application
from .services import can_transition, get_allowed_next_statuses

logger = logging.getLogger(__name__)


@login_required
@role_required(User.Role.CANDIDATE)
def apply_job(request, job_id):
    logger.info(
        "Job application requested. candidate_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        status=Job.JobStatus.PUBLISHED,
    )

    if (
        job.application_deadline
        and job.application_deadline < timezone.now().date()
    ):
        logger.warning(
            "Candidate attempted to apply after deadline. job_id=%s",
            job.id,
        )

        messages.error(
            request,
            "Application deadline has already passed.",
        )

        return redirect("candidate-job-list")

    application, created = Application.objects.get_or_create(
        candidate=request.user,
        job=job,
    )

    if not created:
        logger.warning(
            "Duplicate application prevented. candidate_id=%s job_id=%s",
            request.user.id,
            job.id,
        )

        messages.warning(
            request,
            "You have already applied for this job.",
        )

        return redirect("candidate-job-list")

    logger.info(
        "Application created successfully. application_id=%s",
        application.id,
    )

    messages.success(
        request,
        "Your application has been submitted successfully.",
    )

    return redirect("my-applications")


@login_required
@role_required(User.Role.RECRUITER)
def update_application_status(request, application_id):
    logger.info(
        "Application status update requested. recruiter_id=%s application_id=%s",
        request.user.id,
        application_id,
    )

    application = get_object_or_404(
        Application,
        id=application_id,
        job__company__owner=request.user,
    )

    if request.method == "POST":

        new_status = request.POST.get("status")

        valid_statuses = [choice[0] for choice in Application.Status.choices]

        if new_status not in valid_statuses:
            logger.warning(
                "Invalid application status received. application_id=%s status=%s",
                application.id,
                new_status,
            )

            messages.error(request, "Invalid status value.")

            return redirect(
                "update-application-status",
                application_id=application.id,
            )

        if not can_transition(application.status, new_status):
            logger.warning(
                "Invalid status transition. application_id=%s from=%s to=%s",
                application.id,
                application.status,
                new_status,
            )

            labels = dict(Application.Status.choices)

            messages.error(
                request,
                f"Cannot move an application from "
                f"{labels[application.status]} to {labels[new_status]}.",
            )

            return redirect(
                "update-application-status",
                application_id=application.id,
            )

        old_status = application.status
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])

        logger.info(
            "Application status updated successfully. application_id=%s from=%s to=%s",
            application.id,
            old_status,
            new_status,
        )

        messages.success(
            request,
            "Application status updated successfully.",
        )

        return redirect(
            "job-applicants",
            job_id=application.job.id,
        )

    context = {
        "application": application,
        "status_choices": get_allowed_next_statuses(application.status),
    }

    return render(
        request,
        "applicants/update_status.html",
        context,
    )


@login_required
@role_required(User.Role.CANDIDATE)
def my_applications(request):
    logger.info(
        "Candidate viewed applications. candidate_id=%s",
        request.user.id,
    )

    applications = (
        Application.objects
        .filter(candidate=request.user)
        .select_related("job", "job__company")
        .order_by("-applied_at")
    )

    paginator = Paginator(applications, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    logger.info(
        "Returned %d applications for candidate_id=%s",
        page_obj.paginator.count,
        request.user.id,
    )

    context = {
        "page_obj": page_obj,
        "applications": page_obj.object_list,
    }

    return render(
        request,
        "applicants/my_applications.html",
        context,
    )


@login_required
@role_required(User.Role.RECRUITER)
def recruiter_applications(request, job_id):
    logger.info(
        "Recruiter viewed job applications. recruiter_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        company__owner=request.user,
    )

    applications = (
        Application.objects
        .filter(job=job)
        .select_related("candidate", "job")
        .order_by("-applied_at")
    )

    context = {
        "job": job,
        "applications": applications,
    }

    return render(
        request,
        "applicants/recruiter_applications.html",
        context,
    )


@login_required
@role_required(User.Role.RECRUITER)
def shortlist_candidate(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        job__company__owner=request.user,
    )

    application.status = Application.Status.SCREENING
    application.save(update_fields=["status", "updated_at"])

    logger.info(
        "Candidate shortlisted. application_id=%s recruiter_id=%s",
        application.id,
        request.user.id,
    )

    messages.success(request, "Candidate shortlisted successfully.")

    return redirect(
        "recruiter-applications",
        job_id=application.job.id,
    )


@login_required
@role_required(User.Role.RECRUITER)
def reject_candidate(request, application_id):
    application = get_object_or_404(
        Application,
        id=application_id,
        job__company__owner=request.user,
    )

    application.status = Application.Status.REJECTED
    application.save(update_fields=["status", "updated_at"])

    logger.info(
        "Candidate rejected. application_id=%s recruiter_id=%s",
        application.id,
        request.user.id,
    )

    messages.success(request, "Candidate rejected.")

    return redirect(
        "recruiter-applications",
        job_id=application.job.id,
    )