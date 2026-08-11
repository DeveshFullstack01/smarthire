import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from offers.models import Offer

from .forms import EmployeeOnboardingForm
from .models import EmployeeOnboarding


logger = logging.getLogger(__name__)


# ==========================================================
# Candidate
# ==========================================================

@login_required
@role_required(User.Role.CANDIDATE)
def start_onboarding(request, offer_id):
    """
    Candidate starts or continues onboarding
    for an accepted offer.
    """

    logger.info(
        "Onboarding requested. candidate_id=%s offer_id=%s",
        request.user.id,
        offer_id,
    )

    # ------------------------------------------------------
    # Get offer belonging to logged-in candidate
    # ------------------------------------------------------

    offer = get_object_or_404(
        Offer.objects.select_related(
            "application",
            "application__candidate",
            "application__job",
            "application__job__company",
        ),
        id=offer_id,
        application__candidate=request.user,
    )

    # ------------------------------------------------------
    # Business Rule 1
    # Offer must be accepted
    # ------------------------------------------------------

    if offer.status != Offer.Status.ACCEPTED:

        messages.error(
            request,
            "You can start onboarding only after accepting the offer.",
        )

        return redirect("my-offers")

    # ------------------------------------------------------
    # Get existing onboarding or create it
    # ------------------------------------------------------

    onboarding, created = (
        EmployeeOnboarding.objects.get_or_create(
            offer=offer,
            defaults={
                "candidate": request.user,
            },
        )
    )

    if created:

        logger.info(
            "Onboarding record created. "
            "candidate_id=%s onboarding_id=%s offer_id=%s",
            request.user.id,
            onboarding.id,
            offer.id,
        )

    # ------------------------------------------------------
    # Safety check
    #
    # The onboarding record must belong to this candidate.
    # ------------------------------------------------------

    if onboarding.candidate_id != request.user.id:

        messages.error(
            request,
            "You are not authorized to access this onboarding.",
        )

        logger.warning(
            "Unauthorized onboarding access attempt. "
            "candidate_id=%s onboarding_id=%s",
            request.user.id,
            onboarding.id,
        )

        return redirect("my-offers")

    # ------------------------------------------------------
    # Business Rule 2
    #
    # Approved / Completed onboarding cannot be edited.
    # ------------------------------------------------------

    if onboarding.status in (
        EmployeeOnboarding.Status.APPROVED,
        EmployeeOnboarding.Status.COMPLETED,
    ):

        messages.info(
            request,
            "Your onboarding has already been approved.",
        )

        return redirect("my-onboarding")

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if request.method == "POST":

        form = EmployeeOnboardingForm(
            request.POST,
            instance=onboarding,
        )

        if form.is_valid():

            onboarding = form.save(commit=False)

            # Always enforce the authenticated candidate.
            onboarding.candidate = request.user

            # Candidate submission goes to recruiter review.
            onboarding.status = (
                EmployeeOnboarding.Status.UNDER_REVIEW
            )

            onboarding.save()

            logger.info(
                "Candidate submitted onboarding for review. "
                "candidate_id=%s onboarding_id=%s",
                request.user.id,
                onboarding.id,
            )

            messages.success(
                request,
                "Onboarding information submitted successfully "
                "and is now under recruiter review.",
            )

            return redirect("my-onboarding")

        logger.warning(
            "Onboarding form validation failed. "
            "candidate_id=%s onboarding_id=%s",
            request.user.id,
            onboarding.id,
        )

        messages.error(
            request,
            "Please correct the highlighted errors.",
        )

    else:

        form = EmployeeOnboardingForm(
            instance=onboarding,
        )

    return render(
        request,
        "onboarding/start_onboarding.html",
        {
            "form": form,
            "offer": offer,
            "onboarding": onboarding,
        },
    )


# ==========================================================
# Candidate Dashboard
# ==========================================================

@login_required
@role_required(User.Role.CANDIDATE)
def my_onboarding(request):
    """
    Candidate views their current onboarding progress.
    """

    onboarding = (
        EmployeeOnboarding.objects
        .select_related(
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        )
        .filter(
            candidate=request.user,
        )
        .first()
    )

    return render(
        request,
        "onboarding/my_onboarding.html",
        {
            "onboarding": onboarding,
        },
    )


# ==========================================================
# Recruiter Dashboard
# ==========================================================

@login_required
@role_required(User.Role.RECRUITER)
def recruiter_onboarding(request):
    """
    Recruiter views onboarding records for their company.
    """

    onboarding_records = (
        EmployeeOnboarding.objects
        .select_related(
            "candidate",
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        )
        .filter(
            offer__application__job__company__owner=request.user,
        )
        .order_by(
            "-updated_at",
        )
    )

    context = {
        "onboarding_records": onboarding_records,

        "not_started_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.NOT_STARTED,
        ).count(),

        "in_progress_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.IN_PROGRESS,
        ).count(),

        "under_review_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.UNDER_REVIEW,
        ).count(),

        "approved_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.APPROVED,
        ).count(),

        "rejected_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.REJECTED,
        ).count(),

        "completed_count": onboarding_records.filter(
            status=EmployeeOnboarding.Status.COMPLETED,
        ).count(),
    }

    return render(
        request,
        "onboarding/recruiter_onboarding.html",
        context,
    )

# ==========================================================
# Recruiter Review
# ==========================================================

@login_required
@role_required(User.Role.RECRUITER)
def review_onboarding(request, onboarding_id):
    """
    Recruiter reviews candidate onboarding.
    """

    onboarding = get_object_or_404(
        EmployeeOnboarding.objects.select_related(
            "candidate",
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        ),
        id=onboarding_id,
        offer__application__job__company__owner=request.user,
    )

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------

    if request.method == "GET":

        return render(
            request,
            "onboarding/review_onboarding.html",
            {
                "onboarding": onboarding,
            },
        )

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    action = request.POST.get("action")

    # ======================================================
    # APPROVE
    # ======================================================

    if action == "approve":

        # Only submitted onboarding can be approved.
        if onboarding.status != (
            EmployeeOnboarding.Status.UNDER_REVIEW
        ):

            messages.error(
                request,
                "Only onboarding records under review can be approved.",
            )

            return redirect(
                "recruiter-onboarding",
            )

        onboarding.status = (
            EmployeeOnboarding.Status.APPROVED
        )

        onboarding.rejection_reason = ""

        onboarding.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        logger.info(
            "Onboarding approved. "
            "recruiter_id=%s onboarding_id=%s candidate_id=%s",
            request.user.id,
            onboarding.id,
            onboarding.candidate_id,
        )

        messages.success(
            request,
            "Onboarding has been approved.",
        )

    # ======================================================
    # REJECT
    # ======================================================

    elif action == "reject":

        # Only submitted onboarding can be rejected.
        if onboarding.status != (
            EmployeeOnboarding.Status.UNDER_REVIEW
        ):

            messages.error(
                request,
                "Only onboarding records under review can be rejected.",
            )

            return redirect(
                "recruiter-onboarding",
            )

        rejection_reason = (
            request.POST.get(
                "rejection_reason",
                "",
            )
            .strip()
        )

        if not rejection_reason:

            messages.error(
                request,
                "Please provide a rejection reason.",
            )

            return redirect(
                "review-onboarding",
                onboarding_id=onboarding.id,
            )

        onboarding.status = (
            EmployeeOnboarding.Status.REJECTED
        )

        onboarding.rejection_reason = (
            rejection_reason
        )

        onboarding.save(
            update_fields=[
                "status",
                "rejection_reason",
                "updated_at",
            ]
        )

        logger.info(
            "Onboarding rejected. "
            "recruiter_id=%s onboarding_id=%s candidate_id=%s",
            request.user.id,
            onboarding.id,
            onboarding.candidate_id,
        )

        messages.warning(
            request,
            "Onboarding has been rejected.",
        )

    # ======================================================
    # INVALID ACTION
    # ======================================================

    else:

        messages.error(
            request,
            "Invalid onboarding action.",
        )

    return redirect(
        "recruiter-onboarding",
    )

@login_required
@role_required(User.Role.ADMIN)
def admin_onboarding(request):
    """
    HR/Admin views onboarding records.

    Approved onboarding records are ready for
    final HR/Admin completion.
    """

    onboardings = (
        EmployeeOnboarding.objects
        .select_related(
            "candidate",
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        )
        .order_by(
            "-updated_at",
        )
    )

    context = {
        "onboardings": onboardings,

        "pending_count": onboardings.filter(
            status__in=[
                EmployeeOnboarding.Status.NOT_STARTED,
                EmployeeOnboarding.Status.IN_PROGRESS,
                EmployeeOnboarding.Status.UNDER_REVIEW,
            ],
        ).count(),

        "approved_count": onboardings.filter(
            status=EmployeeOnboarding.Status.APPROVED,
        ).count(),

        "completed_count": onboardings.filter(
            status=EmployeeOnboarding.Status.COMPLETED,
        ).count(),

        "rejected_count": onboardings.filter(
            status=EmployeeOnboarding.Status.REJECTED,
        ).count(),
    }

    return render(
        request,
        "onboarding/admin_onboarding.html",
        context,
    )

# ==========================================================
# Admin - Onboarding Details
# ==========================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_onboarding_detail(request, onboarding_id):
    """
    Admin views complete onboarding information
    for a candidate.

    This page is read-only.
    """
    onboarding = get_object_or_404(
        EmployeeOnboarding.objects.select_related(
            "candidate",
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        ),
        id=onboarding_id,
    )

    return render(
        request,
        "onboarding/admin_onboarding_detail.html",
        {
            "onboarding": onboarding,
        },
    )


# ==========================================================
# HR / Admin Complete Onboarding
# ==========================================================
@login_required
@role_required(User.Role.ADMIN)
def complete_onboarding(request, onboarding_id):

    onboarding = get_object_or_404(
        EmployeeOnboarding.objects.select_related(
            "candidate",
            "offer",
            "offer__application",
            "offer__application__job",
            "offer__application__job__company",
        ),
        id=onboarding_id,
    )

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request.",
        )

        return redirect(
            "admin-onboarding",
        )

    if onboarding.status != EmployeeOnboarding.Status.APPROVED:

        messages.error(
            request,
            "Only approved onboarding records can be completed.",
        )

        return redirect(
            "admin-onboarding",
        )

    onboarding.status = EmployeeOnboarding.Status.COMPLETED

    onboarding.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    logger.info(
        "Employee onboarding completed. "
        "onboarding_id=%s candidate_id=%s admin_id=%s",
        onboarding.id,
        onboarding.candidate.id,
        request.user.id,
    )

    messages.success(
        request,
        "Employee onboarding completed successfully.",
    )

    return redirect(
        "admin-onboarding",
    )
