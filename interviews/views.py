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
from .forms import InterviewFeedbackForm
from .forms import InterviewForm
from .models import Interview

from .forms import (
    InterviewForm,
    InterviewFeedbackForm,
)


logger = logging.getLogger(__name__)


# ==================================================
# Recruiter Views
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

    existing_interview = (
        Interview.objects.filter(
            application=application,
            status=Interview.Status.SCHEDULED,
        )
        .order_by("-scheduled_at")
        .first()
    )

    if existing_interview:

        logger.warning(
            "Recruiter attempted to schedule a duplicate interview. "
            "application_id=%s interview_id=%s",
            application.id,
            existing_interview.id,
        )

        messages.warning(
            request,
            "A scheduled interview already exists for this application.",
        )

        return redirect("recruiter-interviews")

    if request.method == "POST":

        form = InterviewForm(request.POST)

        if form.is_valid():

            interview = form.save(commit=False)
            interview.application = application
            interview.save()

            if application.status != Application.Status.INTERVIEW:

                application.status = Application.Status.INTERVIEW

                application.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            notify(
                recipient=application.candidate,
                message=(
                    f"Interview scheduled for "
                    f"{application.job.title} on "
                    f"{interview.scheduled_at:%d %b %Y, %I:%M %p}."
                ),
                url=f"/interviews/{interview.id}/",
                email_subject="Interview Scheduled",
            )

            logger.info(
                "Interview scheduled successfully. interview_id=%s",
                interview.id,
            )

            messages.success(
                request,
                "Interview scheduled successfully.",
            )

            return redirect("recruiter-interviews")

        logger.warning(
            "Interview form validation failed. recruiter_id=%s",
            request.user.id,
        )

        messages.error(
            request,
            "Please correct the highlighted errors.",
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
def interview_feedback(request, interview_id):

    interview = get_object_or_404(
        Interview.objects.select_related(
            "application",
            "application__candidate",
            "application__job",
            "application__job__company",
        ),
        id=interview_id,
        application__job__company__owner=request.user,
    )

    if request.method == "POST":

        form = InterviewFeedbackForm(
            request.POST,
            instance=interview,
        )

        if form.is_valid():

            interview = form.save(commit=False)

            interview.status = Interview.Status.COMPLETED

            interview.save()

            logger.info(
                "Interview feedback submitted. interview_id=%s",
                interview.id,
            )

            notify(
                recipient=interview.application.candidate,
                message=(
                    f"Your interview feedback for "
                    f"{interview.application.job.title} "
                    f"has been recorded."
                ),
                url=f"/interviews/{interview.id}/",
                email_subject="Interview Completed",
            )

            messages.success(
                request,
                "Interview marked as completed.",
            )

            return redirect(
                "recruiter-interviews",
            )

    else:

        form = InterviewFeedbackForm(
            instance=interview,
        )

    return render(
        request,
        "interviews/interview_feedback.html",
        {
            "form": form,
            "interview": interview,
        },
    )

# ==================================================
# Admin Views
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_interviews(request):
    """
    Admin view for managing all interviews across SmartHire ATS.
    """

    logger.info(
        "Admin interview management requested. admin_id=%s",
        request.user.id,
    )

    interviews = (
        Interview.objects
        .select_related(
            "application",
            "application__candidate",
            "application__job",
            "application__job__company",
        )
        .order_by("-scheduled_at")
    )

    context = {
        "interviews": interviews,

        "total_count": interviews.count(),

        "scheduled_count": interviews.filter(
            status=Interview.Status.SCHEDULED
        ).count(),

        "completed_count": interviews.filter(
            status=Interview.Status.COMPLETED
        ).count(),

        "cancelled_count": interviews.filter(
            status=Interview.Status.CANCELLED
        ).count(),

        "rescheduled_count": interviews.filter(
            status=Interview.Status.RESCHEDULED
        ).count(),
    }

    logger.info(
        "Admin interview list returned %d rows. admin_id=%s",
        interviews.count(),
        request.user.id,
    )

    return render(
        request,
        "interviews/admin_interviews.html",
        context,
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
        .filter(
            application__job__company__owner=request.user
        )
        .order_by("-scheduled_at")
    )
    for interview in interviews:

     interview.can_create_offer = (
        interview.status == Interview.Status.COMPLETED
        and interview.recommendation in [
            Interview.Recommendation.HIRE,
            Interview.Recommendation.STRONG_HIRE,
        ]
        and not hasattr(interview.application, "offer")
    )

    logger.info(
        "Recruiter interview list returned %d rows. recruiter_id=%s",
        interviews.count(),
        request.user.id,
    )

    context = {
        "interviews": interviews,

        "scheduled_count": interviews.filter(
            status=Interview.Status.SCHEDULED
        ).count(),

        "completed_count": interviews.filter(
            status=Interview.Status.COMPLETED
        ).count(),

        "cancelled_count": interviews.filter(
            status=Interview.Status.CANCELLED
        ).count(),
    }

    return render(
        request,
        "interviews/recruiter_interviews.html",
        context,
    )


# ==================================================
# Candidate Views
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
        .filter(
            application__candidate=request.user
        )
        .order_by("-scheduled_at")
    )

    logger.info(
        "Candidate viewed %s interviews.",
        interviews.count(),
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

        interview.candidate_response
        == Interview.CandidateResponse.PENDING

        and

        interview.status not in [

            Interview.Status.COMPLETED,
            Interview.Status.CANCELLED,

        ]

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
@role_required(User.Role.RECRUITER)
def interview_feedback(request, interview_id):
    """
    Recruiter submits interview feedback after the interview.
    """

    interview = get_object_or_404(
        Interview.objects.select_related(
            "application",
            "application__candidate",
            "application__job",
            "application__job__company",
        ),
        id=interview_id,
        application__job__company__owner=request.user,
    )

    if request.method == "POST":

        form = InterviewFeedbackForm(
            request.POST,
            instance=interview,
        )

        if form.is_valid():

            interview = form.save()

            interview.status = Interview.Status.COMPLETED
            interview.save(update_fields=[
                "status",
                "overall_rating",
                "technical_rating",
                "communication_rating",
                "problem_solving_rating",
                "recommendation",
                "feedback",
                "updated_at",
            ])

            application = interview.application

            if (
                interview.recommendation
                == Interview.Recommendation.STRONG_HIRE
            ):
                application.status = Application.Status.OFFER

            elif (
                interview.recommendation
                == Interview.Recommendation.HIRE
            ):
                application.status = Application.Status.OFFER

            elif (
                interview.recommendation
                == Interview.Recommendation.HOLD
            ):
                application.status = Application.Status.INTERVIEW

            else:
                application.status = Application.Status.REJECTED

            application.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            notify(
                recipient=application.candidate,
                message=(
                    f"Your interview for "
                    f"{application.job.title} "
                    f"has been evaluated."
                ),
                url=f"/interviews/{interview.id}/",
                email_subject="Interview Feedback",
            )

            logger.info(
                "Interview feedback submitted. interview_id=%s",
                interview.id,
            )

            messages.success(
                request,
                "Interview feedback submitted successfully.",
            )

            return redirect("recruiter-interviews")

    else:

        form = InterviewFeedbackForm(
            instance=interview,
        )

    return render(
        request,
        "interviews/interview_feedback.html",
        {
            "form": form,
            "interview": interview,
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

    response = request.POST.get(
        "response",
        "",
    ).strip()

    note = request.POST.get(
        "note",
        "",
    ).strip()

    valid_responses = {

        Interview.CandidateResponse.ACCEPTED,
        Interview.CandidateResponse.DECLINED,
        Interview.CandidateResponse.RESCHEDULE,

    }

    if response not in valid_responses:

        messages.error(
            request,
            "Invalid interview response.",
        )

        return redirect(
            "interview-detail",
            interview_id=interview.id,
        )

    if interview.status in [

        Interview.Status.COMPLETED,
        Interview.Status.CANCELLED,

    ]:

        messages.error(
            request,
            "This interview is already closed.",
        )

        return redirect(
            "interview-detail",
            interview_id=interview.id,
        )

    if (
        interview.candidate_response
        != Interview.CandidateResponse.PENDING
    ):

        messages.warning(
            request,
            "You have already responded.",
        )

        return redirect(
            "interview-detail",
            interview_id=interview.id,
        )

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

    recruiter = interview.application.job.company.owner

    notify(
        recipient=recruiter,
        message=(
            f"{request.user.username} "
            f"responded '{response}' "
            f"for the interview "
            f"of {interview.application.job.title}."
        ),
        url=f"/interviews/{interview.id}/",
        email_subject="Interview Response Received",
    )

    logger.info(
        "Interview response recorded. interview_id=%s response=%s",
        interview.id,
        response,
    )

    messages.success(
        request,
        "Your response has been recorded successfully.",
    )

    return redirect(
        "interview-detail",
        interview_id=interview.id,
    )