import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from applicants.models import Application
from interviews.models import Interview
from notifications.services import notify

from .forms import OfferForm
from .models import Offer

from django.core.files.base import ContentFile

from .pdf_generator import generate_offer_letter

logger = logging.getLogger(__name__)


# ==========================================================
@login_required
@role_required(User.Role.RECRUITER)
def create_offer(request, application_id):
    print("========== CREATE OFFER VIEW ==========")
    print("METHOD:", request.method)

    logger.info(
        "Create offer requested. recruiter_id=%s application_id=%s",
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

    # ==========================================
    # Latest Interview
    # ==========================================

    interview = (
        application.interviews
        .order_by("-scheduled_at")
        .first()
    )

    # ==========================================
    # Business Rule 1
    # ==========================================

    if not interview:

        messages.error(
            request,
            "No interview has been scheduled for this candidate.",
        )

        return redirect(
            "job-applicants",
            job_id=application.job.id,
        )

    # ==========================================
    # Business Rule 2
    # ==========================================

    if interview.status != Interview.Status.COMPLETED:

        messages.error(
            request,
            "Interview must be completed before creating an offer.",
        )

        return redirect(
            "job-applicants",
            job_id=application.job.id,
        )

    # ==========================================
    # Business Rule 3
    # ==========================================

    if interview.recommendation not in (
        Interview.Recommendation.HIRE,
        Interview.Recommendation.STRONG_HIRE,
    ):

        messages.error(
            request,
            "Candidate is not recommended for hiring.",
        )

        return redirect(
            "job-applicants",
            job_id=application.job.id,
        )

    # ==========================================
    # Business Rule 4
    # ==========================================

    if hasattr(application, "offer"):

        messages.warning(
            request,
            "An offer has already been created for this application.",
        )

        return redirect(
            "recruiter-offers",
        )

    # ==========================================
    # Handle Form
    # ==========================================

    if request.method == "POST":

        form = OfferForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            # --------------------------------------
            # Save Offer
            # --------------------------------------

            offer = form.save(commit=False)
            offer.application = application
            offer.save()

            # --------------------------------------
            # Generate Offer Letter PDF
            # --------------------------------------

            pdf_buffer = generate_offer_letter(offer)

            offer.offer_letter.save(
                f"offer_{offer.id}.pdf",
                ContentFile(pdf_buffer.read()),
                save=True,
            )

            logger.info(
                "Offer PDF generated successfully. offer_id=%s",
                offer.id,
            )

            # --------------------------------------
            # Update Application Status
            # --------------------------------------

            application.status = Application.Status.OFFER

            application.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            # --------------------------------------
            # Notify Candidate
            # --------------------------------------

            notify(
                recipient=application.candidate,
                message=(
                    f"You have received an offer for "
                    f"{application.job.title}."
                ),
                url="/offers/my/",
                email_subject="Job Offer Received",
            )

            logger.info(
                "Offer created successfully. offer_id=%s",
                offer.id,
            )

            messages.success(
                request,
                "Offer created successfully. Offer letter PDF generated successfully.",
            )

            return redirect(
                "recruiter-offers",
            )

        logger.warning(
            "Offer form validation failed. application_id=%s",
            application.id,
        )

        messages.error(
            request,
            "Please correct the highlighted errors.",
        )

    else:

        form = OfferForm(
            initial={
                "designation": application.job.title,
            }
        )

    return render(
        request,
        "offers/create_offer.html",
        {
            "form": form,
            "application": application,
        },
    )


# ==========================================================
# Recruiter Dashboard
# ==========================================================

@login_required
@role_required(User.Role.RECRUITER)
def recruiter_offers(request):

    offers = (
        Offer.objects.select_related(
            "application",
            "application__candidate",
            "application__job",
        )
        .filter(
            application__job__company__owner=request.user,
        )
        .order_by("-created_at")
    )

    context = {
        "offers": offers,
        "pending_count": offers.filter(
            status=Offer.Status.PENDING,
        ).count(),
        "accepted_count": offers.filter(
            status=Offer.Status.ACCEPTED,
        ).count(),
        "rejected_count": offers.filter(
            status=Offer.Status.REJECTED,
        ).count(),
        "expired_count": offers.filter(
            status=Offer.Status.EXPIRED,
        ).count(),
    }

    return render(
        request,
        "offers/recruiter_offers.html",
        context,
    )


# ==========================================================
# Candidate Dashboard
# ==========================================================

@login_required
@role_required(User.Role.CANDIDATE)
def my_offers(request):

    offers = (
        Offer.objects.select_related(
            "application",
            "application__job",
        )
        .filter(
            application__candidate=request.user,
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "offers/my_offers.html",
        {
            "offers": offers,
        },
    )


# ==========================================================
# Candidate Response
# ==========================================================

@login_required
@role_required(User.Role.CANDIDATE)
def respond_offer(request, offer_id, action):

    offer = get_object_or_404(
        Offer,
        id=offer_id,
        application__candidate=request.user,
    )

    if offer.is_expired:

        offer.status = Offer.Status.EXPIRED

        offer.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        messages.error(
            request,
            "Offer has expired.",
        )

        return redirect(
            "my-offers",
        )

    if offer.status != Offer.Status.PENDING:

        messages.warning(
            request,
            "You have already responded.",
        )

        return redirect(
            "my-offers",
        )

    if action == "accept":

        offer.status = Offer.Status.ACCEPTED

    elif action == "reject":

        offer.status = Offer.Status.REJECTED

    else:

        messages.error(
            request,
            "Invalid action.",
        )

        return redirect(
            "my-offers",
        )

    offer.responded_at = timezone.now()

    offer.save(
        update_fields=[
            "status",
            "responded_at",
            "updated_at",
        ]
    )

    recruiter = offer.application.job.company.owner

    notify(
        recipient=recruiter,
        message=(
            f"{request.user.username} "
            f"{offer.status.lower()} the offer."
        ),
        url="/offers/recruiter/",
        email_subject="Offer Response",
    )

    messages.success(
        request,
        "Your response has been recorded.",
    )

    return redirect(
        "my-offers",
    )
