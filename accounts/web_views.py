import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from jobs.models import Job

from .models import User

logger = logging.getLogger(__name__)


def login_page(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(
                request,
                "Invalid username or password.",
            )
            return render(request, "login.html")

        if not user.is_verified:
            messages.error(
                request,
                "Please verify your email first.",
            )
            return render(request, "login.html")

        login(request, user)

        logger.info(
            "User %s logged in successfully.",
            user.username,
        )

        return redirect_user(user)

    return render(request, "login.html")


def logout_page(request):

    logout(request)

    return redirect("web-login")


def redirect_user(user):

    if user.role == User.Role.ADMIN:
        return redirect("admin-dashboard")

    if user.role == User.Role.RECRUITER:
        return redirect("recruiter-dashboard")

    return redirect("candidate-dashboard")


@role_required(User.Role.ADMIN)
def admin_dashboard(request):

    return render(
        request,
        "admin/dashboard.html",
    )

@login_required
@role_required(User.Role.CANDIDATE)
def candidate_dashboard(request):

    return render(
        request,
        "candidate/dashboard.html",
    )
    
@login_required
@role_required(User.Role.CANDIDATE)
def candidate_dashboard(request):
    from .candidate_dashboard_service import get_candidate_dashboard_data

    context = get_candidate_dashboard_data(request.user)

    return render(
        request,
        "candidate/dashboard.html",
        context,
    )