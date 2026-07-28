from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import JobForm
from .models import Company


@login_required
@role_required(User.Role.RECRUITER)
def create_job(request):
    """
    Allow recruiters to create a new job.
    """

    company = Company.objects.filter(
        owner=request.user
    ).first()

    if company is None:
        messages.error(
            request,
            "No company is linked to your account."
        )
        return redirect("recruiter-dashboard")

    if request.method == "POST":

        form = JobForm(request.POST)

        if form.is_valid():

            job = form.save(commit=False)

            job.company = company

            job.save()

            messages.success(
                request,
                "Job created successfully."
            )

            return redirect("recruiter-dashboard")

    else:

        form = JobForm()

    return render(
        request,
        "jobs/create_job.html",
        {
            "form": form,
        },
    )