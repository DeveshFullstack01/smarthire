import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from applicants.models import Application

from .forms import JobForm
from .models import Job

logger = logging.getLogger(__name__)


# ==================================================
# Candidate
# ==================================================

@login_required
@role_required(User.Role.CANDIDATE)
def candidate_job_list(request):

    logger.info(
        "Candidate job list requested. user_id=%s",
        request.user.id,
    )

    jobs = (
        Job.objects
        .filter(status=Job.JobStatus.PUBLISHED)
        .select_related("company")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    location = request.GET.get("location", "").strip()

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__name__icontains=search)
        )

    if location:
        jobs = jobs.filter(
            location__icontains=location
        )

    paginator = Paginator(jobs, 10)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "search": search,
        "location": location,
    }

    return render(
        request,
        "jobs/candidate_job_list.html",
        context,
    )


# ==================================================
# Create Job
# Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def create_job(request):

    logger.info(
        "Create job page opened. user_id=%s role=%s",
        request.user.id,
        request.user.role,
    )

    # --------------------------------------------------
    # Admin
    # --------------------------------------------------

    if request.user.role == User.Role.ADMIN:

        if request.method == "POST":

            form = JobForm(request.POST)

            if form.is_valid():

                job = form.save()

                logger.info(
                    "Admin created job. job_id=%s admin_id=%s",
                    job.id,
                    request.user.id,
                )

                messages.success(
                    request,
                    "Job created successfully.",
                )

                return redirect("job-list")

        else:

            form = JobForm()

        return render(
            request,
            "jobs/create_job.html",
            {"form": form},
        )

    # --------------------------------------------------
    # Recruiter
    # --------------------------------------------------

    company = request.user.companies.first()

    if company is None:

        logger.warning(
            "Recruiter has no company. recruiter_id=%s",
            request.user.id,
        )

        messages.error(
            request,
            "No company is associated with your account.",
        )

        return redirect(
            "recruiter-dashboard"
        )

    if request.method == "POST":

        form = JobForm(request.POST)

        if form.is_valid():

            job = form.save(
                commit=False
            )

            job.company = company
            job.save()

            messages.success(
                request,
                "Job created successfully.",
            )

            return redirect(
                "recruiter-dashboard"
            )

    else:

        form = JobForm()

    return render(
        request,
        "jobs/create_job.html",
        {"form": form},
    )


# ==================================================
# Job List
# Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def job_list(request):

    logger.info(
        "Job list requested. user_id=%s role=%s",
        request.user.id,
        request.user.role,
    )

    # --------------------------------------------------
    # Admin sees ALL jobs
    # --------------------------------------------------

    if request.user.role == User.Role.ADMIN:

        jobs = (
            Job.objects
            .select_related("company")
            .order_by("-created_at")
        )

    # --------------------------------------------------
    # Recruiter sees ONLY their company's jobs
    # --------------------------------------------------

    else:

        jobs = (
            Job.objects
            .filter(
                company__owner=request.user
            )
            .select_related("company")
            .order_by("-created_at")
        )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    location = request.GET.get(
        "location",
        "",
    ).strip()

    if search:

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
        )

    if status:

        jobs = jobs.filter(
            status=status
        )

    if location:

        jobs = jobs.filter(
            location__icontains=location
        )

    paginator = Paginator(
        jobs,
        10,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "search": search,
        "status": status,
        "location": location,
        "status_choices": Job.JobStatus.choices,
    }

    return render(
        request,
        "jobs/job_list.html",
        context,
    )


# ==================================================
# Job Detail
# Candidate + Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.CANDIDATE,
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def job_detail(request, job_id):

    job = get_object_or_404(
        Job.objects.select_related(
            "company"
        ),
        id=job_id,
    )

    has_applied = False

    if request.user.role == User.Role.CANDIDATE:

        has_applied = Application.objects.filter(
            candidate=request.user,
            job=job,
        ).exists()

    context = {
        "job": job,
        "has_applied": has_applied,
    }

    return render(
        request,
        "jobs/job_detail.html",
        context,
    )

# ==========================================================
# Admin Job Management
# ==========================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_job_list(request):
    """
    Admin-only job management page.

    Admin can view all jobs across all companies.
    """

    logger.info(
        "Admin job list requested. admin_id=%s",
        request.user.id,
    )

    jobs = (
        Job.objects
        .select_related("company")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    location = request.GET.get("location", "").strip()

    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    if search:

        logger.debug(
            "Admin filtering jobs by search='%s'",
            search,
        )

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(company__name__icontains=search)
        )

    # ------------------------------------------------------
    # Status filter
    # ------------------------------------------------------

    if status:

        logger.debug(
            "Admin filtering jobs by status='%s'",
            status,
        )

        jobs = jobs.filter(
            status=status
        )

    # ------------------------------------------------------
    # Location filter
    # ------------------------------------------------------

    if location:

        logger.debug(
            "Admin filtering jobs by location='%s'",
            location,
        )

        jobs = jobs.filter(
            location__icontains=location
        )

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    paginator = Paginator(
        jobs,
        10,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    logger.info(
        "Admin job list returned %d jobs.",
        page_obj.paginator.count,
    )

    context = {
        "page_obj": page_obj,
        "jobs": page_obj.object_list,
        "search": search,
        "status": status,
        "location": location,
        "status_choices": Job.JobStatus.choices,
        "total_jobs": Job.objects.count(),
        "published_jobs": Job.objects.filter(
            status=Job.JobStatus.PUBLISHED
        ).count(),
    }

    return render(
        request,
        "admin/admin_job_list.html",
        context,
    )

# ==================================================
# Update Job
# Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def update_job(request, job_id):

    # --------------------------------------------------
    # Admin can update any job
    # --------------------------------------------------

    if request.user.role == User.Role.ADMIN:

        job = get_object_or_404(
            Job,
            id=job_id,
        )

    # --------------------------------------------------
    # Recruiter can update only own company job
    # --------------------------------------------------

    else:

        job = get_object_or_404(
            Job,
            id=job_id,
            company__owner=request.user,
        )

    if request.method == "POST":

        form = JobForm(
            request.POST,
            instance=job,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Job updated successfully.",
            )

            return redirect(
                "job-list"
            )

    else:

        form = JobForm(
            instance=job
        )

    return render(
        request,
        "jobs/job_update.html",
        {
            "form": form,
            "job": job,
        },
    )


# ==================================================
# Delete Job
# Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def delete_job(request, job_id):

    # Admin can delete any job
    if request.user.role == User.Role.ADMIN:

        job = get_object_or_404(
            Job,
            id=job_id,
        )

    # Recruiter only own job
    else:

        job = get_object_or_404(
            Job,
            id=job_id,
            company__owner=request.user,
        )

    if request.method == "POST":

        job.delete()

        messages.success(
            request,
            "Job deleted successfully.",
        )

        return redirect(
            "job-list"
        )

    return render(
        request,
        "jobs/delete_job.html",
        {
            "job": job
        },
    )


# ==================================================
# Job Applicants
# Recruiter + Admin
# ==================================================

@login_required
@role_required(
    User.Role.RECRUITER,
    User.Role.ADMIN,
)
def job_applicants(request, job_id):

    # Admin can see applicants for ANY job
    if request.user.role == User.Role.ADMIN:

        job = get_object_or_404(
            Job,
            id=job_id,
        )

    # Recruiter only own company's jobs
    else:

        job = get_object_or_404(
            Job,
            id=job_id,
            company__owner=request.user,
        )

    applications = (
        Application.objects
        .filter(job=job)
        .select_related("candidate")
        .order_by("-applied_at")
    )

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if status:

        applications = applications.filter(
            status=status
        )

    paginator = Paginator(
        applications,
        10,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "job": job,
        "page_obj": page_obj,
        "applications": page_obj.object_list,
        "status": status,
        "status_choices": Application.Status.choices,
    }

    return render(
        request,
        "jobs/job_applicants.html",
        context,
    )