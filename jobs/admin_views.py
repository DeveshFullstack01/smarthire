import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import JobForm
from .models import Job


logger = logging.getLogger(__name__)


# ==================================================
# Admin - Job List
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_job_list(request):

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

    if search:

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(company__name__icontains=search)
        )

    if status:
        jobs = jobs.filter(status=status)

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

        "total_jobs": Job.objects.count(),

        "published_jobs": Job.objects.filter(
            status=Job.JobStatus.PUBLISHED
        ).count(),

        "search": search,
        "status": status,
        "location": location,

        "status_choices": Job.JobStatus.choices,
    }

    return render(
        request,
        "jobs/admin_job_list.html",
        context,
    )


# ==================================================
# Admin - Job Detail
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_job_detail(request, job_id):

    logger.info(
        "Admin viewing job. admin_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job.objects.select_related("company"),
        id=job_id,
    )

    return render(
        request,
        "jobs/admin_job_detail.html",
        {
            "job": job,
        },
    )


# ==================================================
# Admin - Edit Job
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_edit_job(request, job_id):

    logger.info(
        "Admin editing job. admin_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
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

            logger.info(
                "Admin updated job successfully. job_id=%s",
                job.id,
            )

            return redirect(
                "admin-job-list"
            )

    else:

        form = JobForm(
            instance=job
        )

    return render(
        request,
        "jobs/admin_edit_job.html",
        {
            "form": form,
            "job": job,
        },
    )


# ==================================================
# Admin - Delete Job
# ==================================================

@login_required
@role_required(User.Role.ADMIN)
def admin_delete_job(request, job_id):

    logger.info(
        "Admin delete requested. admin_id=%s job_id=%s",
        request.user.id,
        job_id,
    )

    job = get_object_or_404(
        Job,
        id=job_id,
    )

    if request.method == "POST":

        job_title = job.title

        job.delete()

        messages.success(
            request,
            f"Job '{job_title}' deleted successfully.",
        )

        logger.info(
            "Admin deleted job successfully. job_id=%s",
            job_id,
        )

        return redirect(
            "admin-job-list"
        )

    return render(
        request,
        "jobs/admin_delete_job.html",
        {
            "job": job,
        },
    )