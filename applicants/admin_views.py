import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import User
from jobs.models import Job

from .models import Application


logger = logging.getLogger(__name__)


# ==================================================
# Admin - Application Management
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_application_list(request):

    logger.info(
        "Admin application list requested. admin_id=%s",
        request.user.id,
    )

    applications = (
        Application.objects
        .select_related(
            "candidate",
            "job",
            "job__company",
        )
        .order_by("-applied_at")
    )

    # ==================================================
    # Filters
    # ==================================================

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    job_id = request.GET.get(
        "job",
        "",
    ).strip()


    # ==================================================
    # Search
    # ==================================================

    if search:

        applications = applications.filter(
            Q(candidate__username__icontains=search)
            | Q(candidate__email__icontains=search)
            | Q(job__title__icontains=search)
            | Q(job__company__name__icontains=search)
        )


    # ==================================================
    # Status Filter
    # ==================================================

    if status:

        applications = applications.filter(
            status=status
        )


    # ==================================================
    # Job Filter
    # ==================================================

    selected_job = None

    if job_id:

        try:

            selected_job = Job.objects.get(
                id=job_id
            )

            applications = applications.filter(
                job=selected_job
            )

        except Job.DoesNotExist:

            selected_job = None


    # ==================================================
    # Pagination
    # ==================================================

    paginator = Paginator(
        applications,
        10,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )


    # ==================================================
    # Statistics
    # ==================================================

    total_applications = Application.objects.count()

    pending_applications = Application.objects.filter(
        status=Application.Status.APPLIED
    ).count()

    screening_applications = Application.objects.filter(
        status=Application.Status.SCREENING
    ).count()

    interview_applications = Application.objects.filter(
        status=Application.Status.INTERVIEW
    ).count()

    offer_applications = Application.objects.filter(
        status=Application.Status.OFFER
    ).count()

    rejected_applications = Application.objects.filter(
        status=Application.Status.REJECTED
    ).count()


    # ==================================================
    # Context
    # ==================================================

    context = {

        "page_obj": page_obj,

        "applications": page_obj.object_list,

        "jobs": Job.objects
        .select_related("company")
        .order_by("-created_at"),

        "selected_job": selected_job,

        "search": search,

        "status": status,

        "status_choices": Application.Status.choices,

        "total_applications": total_applications,

        "pending_applications": pending_applications,

        "screening_applications": screening_applications,

        "interview_applications": interview_applications,

        "offer_applications": offer_applications,

        "rejected_applications": rejected_applications,
    }


    return render(
        request,
        "applicants/admin_application_list.html",
        context,
    )