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


@login_required
@role_required(User.Role.CANDIDATE)
def candidate_job_list(request):
    logger.info(
        "Candidate job list requested. user_id=%s",
        request.user.id,
    )

    jobs = (
        Job.objects
        .select_related("company")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    location = request.GET.get("location", "").strip()

    if search:
        logger.debug("Searching jobs with keyword='%s'", search)

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company__name__icontains=search)
        )

    if location:
        logger.debug("Filtering jobs by location='%s'", location)

        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    logger.info(
        "Candidate job list returned %d jobs.",
        page_obj.paginator.count,
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


@login_required
@role_required(User.Role.RECRUITER)
def create_job(request):
    logger.info(
        "Create job page opened. recruiter_id=%s",
        request.user.id,
    )

    company = request.user.companies.first()

    if company is None:
        logger.warning(
            "Recruiter has no associated company. recruiter_id=%s",
            request.user.id,
        )

        messages.error(
            request,
            "No company is associated with your account.",
        )
        return redirect("recruiter-dashboard")

    if request.method == "POST":

        form = JobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()

            logger.info(
                "Job created successfully. job_id=%s recruiter_id=%s",
                job.id,
                request.user.id,
            )

            messages.success(request, "Job created successfully.")
            return redirect("recruiter-dashboard")

        logger.warning(
            "Job creation failed due to validation errors. recruiter_id=%s",
            request.user.id,
        )

    else:
        form = JobForm()

    return render(
        request,
        "jobs/create_job.html",
        {"form": form},
    )

@login_required
@role_required(User.Role.RECRUITER)
def job_list(request):
    logger.info(
        "Recruiter job list requested. recruiter_id=%s",
        request.user.id,
    )

    jobs = (
        Job.objects
        .filter(company__owner=request.user)
        .select_related("company")
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    location = request.GET.get("location", "").strip()

    if search:
        logger.debug(
            "Filtering jobs by search='%s'",
            search,
        )

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
        )

    if status:
        logger.debug(
            "Filtering jobs by status='%s'",
            status,
        )

        jobs = jobs.filter(status=status)

    if location:
        logger.debug(
            "Filtering jobs by location='%s'",
            location,
        )

        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    logger.info(
        "Recruiter has %d matching jobs.",
        page_obj.paginator.count,
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


@login_required
@role_required(User.Role.RECRUITER)
def job_detail(request, job_id):
    logger.info(
        "Viewing job details. recruiter_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job.objects.select_related("company"),
        id=job_id,
        company__owner=request.user,
    )

    return render(
        request,
        "jobs/job_detail.html",
        {"job": job},
    )


@login_required
@role_required(User.Role.RECRUITER)
def update_job(request, job_id):
    logger.info(
        "Updating job. recruiter_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        company__owner=request.user,
    )

    if request.method == "POST":

        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()

            logger.info(
                "Job updated successfully. job_id=%s",
                job.id,
            )

            messages.success(request, "Job updated successfully.")
            return redirect("job-list")

        logger.warning(
            "Job update validation failed. job_id=%s",
            job.id,
        )

    else:
        form = JobForm(instance=job)

    return render(
        request,
        "jobs/job_update.html",
        {
            "form": form,
            "job": job,
        },
    )


@login_required
@role_required(User.Role.RECRUITER)
def delete_job(request, job_id):
    logger.info(
        "Delete job requested. recruiter_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        company__owner=request.user,
    )

    if request.method == "POST":
        job.delete()

        logger.info(
            "Job deleted successfully. job_id=%s",
            job_id,
        )

        messages.success(request, "Job deleted successfully.")
        return redirect("job-list")

    return render(
        request,
        "jobs/delete_job.html",
        {"job": job},
    )


@login_required
@role_required(User.Role.RECRUITER)
def job_applicants(request, job_id):
    logger.info(
        "Viewing applicants. recruiter_id=%s job_id=%s",
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
        .select_related("candidate")
        .order_by("-applied_at")
    )

    status = request.GET.get("status", "").strip()

    if status:
        logger.debug(
            "Filtering applicants by status='%s'",
            status,
        )

        applications = applications.filter(status=status)

    paginator = Paginator(applications, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    logger.info(
        "Returned %d applicants for job_id=%s",
        page_obj.paginator.count,
        job.id,
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