import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from accounts.decorators import role_required
from accounts.models import User

from jobs.models import Job

from .models import Application

logger = logging.getLogger(__name__)


@login_required
@role_required(User.Role.CANDIDATE)
def apply_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        status=Job.JobStatus.PUBLISHED,
    )

    application_exists = Application.objects.filter(
        candidate=request.user,
        job=job,
    ).exists()

    if application_exists:

        messages.warning(
            request,
            "You have already applied for this job.",
        )

        return redirect("candidate-job-list")

    Application.objects.create(
        candidate=request.user,
        job=job,
    )

    logger.info(
        "Application submitted. candidate=%s job=%s",
        request.user.id,
        job.id,
    )

    messages.success(
        request,
        "Application submitted successfully.",
    )

    return redirect("candidate-job-list")