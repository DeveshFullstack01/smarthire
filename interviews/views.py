import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User
from applicants.models import Application
from notifications.services import notify

from .forms import InterviewForm
from .models import Interview

logger = logging.getLogger(__name__)


# ==================================================
# Recruiter views
# ==================================================

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

            notify(
                recipient=application.candidate,
                message=(
                    f"Interview scheduled for {application.job.title} "
                    f"on {interview.scheduled_at:%d %b %Y, %H:%M}."
                ),
                url=f"/interviews/{interview.id}/",
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
        notify(
                recipient=application.candidate,
                message=(
                    f"Interview scheduled for {application.job.title} "
                    f"on {interview.scheduled_at:%d %b %Y, %H:%M}."
                ),
                url=f"/interviews/{interview.id}/",
                email_subject="Your interview has been scheduled",
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


# ==================================================
# Candidate views
# ==================================================

@login_required
@role_required(User.Role.CANDIDATE)
def candidate_interviews(request):

    interviews = (
        Interview.objects
        .select_related(
            "application",
            "application__job",
            "application__job__company",
        )
        .filter(application__candidate=request.user)
        .order_by("-scheduled_at")
    )

    logger.info(
        "Candidate interview list returned %d rows. candidate_id=%s",
        interviews.count(),
        request.user.id,
    )

    return render(
        request,
        "interviews/candidate_interviews.html",
        {
            "interviews": interviews,
        },
    )


@login_required
@role_required(User.Role.CANDIDATE)
def interview_detail(request, interview_id):

    interview = get_object_or_404(
        Interview.objects.select_related(
            "application",
            "application__job",
            "application__job__company",
        ),
        id=interview_id,
        application__candidate=request.user,
    )

    can_respond = (
        interview.candidate_response == Interview.CandidateResponse.PENDING
        and interview.status not in (
            Interview.Status.COMPLETED,
            Interview.Status.CANCELLED,
        )
    )

    return render(
        request,
        "interviews/interview_detail.html",
        {
            "interview": interview,
            "can_respond": can_respond,
        },
    )


@login_required
@role_required(User.Role.CANDIDATE)
@require_POST
def respond_to_interview(request, interview_id):

    interview = get_object_or_404(
        Interview,
        id=interview_id,
        application__candidate=request.user,
    )

    response = request.POST.get("response", "").strip()
    note = request.POST.get("note", "").strip()

    valid_responses = {
        Interview.CandidateResponse.ACCEPTED,
        Interview.CandidateResponse.DECLINED,
        Interview.CandidateResponse.RESCHEDULE,
    }

    if response not in valid_responses:
        messages.error(request, "Invalid response.")
        return redirect("interview-detail", interview_id=interview.id)

    if interview.status in (
        Interview.Status.COMPLETED,
        Interview.Status.CANCELLED,
    ):
        messages.error(
            request,
            "This interview is closed and can no longer be updated.",
        )
        return redirect("interview-detail", interview_id=interview.id)

    if interview.candidate_response != Interview.CandidateResponse.PENDING:
        messages.warning(
            request,
            "You have already responded to this interview.",
        )
        return redirect("interview-detail", interview_id=interview.id)

    interview.candidate_response = response
    interview.candidate_note = note
    interview.responded_at = timezone.now()

    if response == Interview.CandidateResponse.RESCHEDULE:
        interview.status = Interview.Status.RESCHEDULED
    elif response == Interview.CandidateResponse.DECLINED:
        interview.status = Interview.Status.CANCELLED

    interview.save(
        update_fields=[
            "candidate_response",
            "candidate_note",
            "responded_at",
            "status",
            "updated_at",
        ]
    )

    logger.info(
        "Candidate responded to interview. interview_id=%s response=%s",
        interview.id,
        response,
    )

    recruiter = interview.application.job.company.owner

    notify(
        recipient=recruiter,
        message=(
            f"{request.user.username} responded '{response}' to the "
            f"interview for {interview.application.job.title}."
        ),
        url=f"/interviews/{interview.id}/",
        email_subject="A candidate responded to an interview",
    )
    messages.success(request, "Your response has been recorded.")

    return redirect("interview-detail", interview_id=interview.id)