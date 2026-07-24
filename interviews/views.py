import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from applicants.models import Application

from .forms import InterviewForm
from .models import Interview

logger = logging.getLogger(__name__)


@login_required
@role_required(User.Role.RECRUITER)
def schedule_interview(request, application_id):
    logger.info(
        "Schedule interview page opened. recruiter_id=%s application_id=%s",
        request.user.id,
        application_id,
    )

    application = get_object_or_404(
        Application.objects.select_related(
            "candidate",
            "job",
            "job__company",
        ),
        id=application_id,
        job__company__owner=request.user,
    )

    if request.method == "POST":

        form = InterviewForm(request.POST)

        if form.is_valid():

            interview = form.save(commit=False)
            interview.application = application
            interview.save()

            logger.info(
                "Interview scheduled. interview_id=%s application_id=%s",
                interview.id,
                application.id,
            )

            messages.success(
                request,
                "Interview scheduled successfully.",
            )

            return redirect("recruiter-interviews")

        logger.warning(
            "Interview scheduling failed validation. application_id=%s",
            application.id,
        )

        messages.error(
            request,
            "Please correct the errors below.",
        )

    else:
        form = InterviewForm()

    return render(
        request,
        "interviews/schedule_interview.html",
        {
            "form": form,
            "application": application,
        },
    )


@login_required
@role_required(User.Role.RECRUITER)
def recruiter_interviews(request):

    interviews = (
        Interview.objects
        .select_related(
            "application",
            "application__candidate",
            "application__job",
            "application__job__company",
        )
        .filter(application__job__company__owner=request.user)
        .order_by("-scheduled_at")
    )

    logger.info(
        "Recruiter interview list returned %d rows. recruiter_id=%s",
        interviews.count(),
        request.user.id,
    )

    return render(
        request,
        "interviews/recruiter_interviews.html",
        {
            "interviews": interviews,
        },
    )