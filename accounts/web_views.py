import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from jobs.models import Job

from .models import User
# ==================================================
# Web signup pages (styled HTML forms)
# ==================================================

from .serializers import CandidateSignupSerializer, RecruiterSignupSerializer


def _render_signup_errors(request, template, serializer):
    """Flash the first error from each field so the HTML form can show them."""
    for field, errors in serializer.errors.items():
        label = field.replace("_", " ").title()
        messages.error(request, f"{label}: {errors[0]}")
    return render(request, template)


def candidate_signup_page(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":
        serializer = CandidateSignupSerializer(
            data={
                "username": request.POST.get("username", ""),
                "email": request.POST.get("email", ""),
                "password": request.POST.get("password", ""),
            }
        )

        if serializer.is_valid():
            from .views import send_verification_email
            user = serializer.save()
            send_verification_email(user)
            logger.info("Candidate signed up via web. user_id=%s", user.id)
            messages.success(
                request,
                "Account created. Check your email to verify, then log in.",
            )
            return redirect("registration-success")

        return _render_signup_errors(
            request, "accounts/candidate_signup.html", serializer
        )

    return render(request, "accounts/candidate_signup.html")


def recruiter_signup_page(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":
        serializer = RecruiterSignupSerializer(
            data={
                "username": request.POST.get("username", ""),
                "email": request.POST.get("email", ""),
                "password": request.POST.get("password", ""),
                "company_name": request.POST.get("company_name", ""),
            }
        )

        if serializer.is_valid():
            from .views import send_verification_email
            user = serializer.save()
            send_verification_email(user)
            logger.info("Recruiter signed up via web. user_id=%s", user.id)
            messages.success(
                request,
                "Account created. Check your email to verify, then log in.",
            )
            return redirect("registration-success")

        return _render_signup_errors(
            request, "accounts/recruiter_signup.html", serializer
        )

    return render(request, "accounts/recruiter_signup.html")

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

@login_required
@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    from .admin_dashboard_service import get_admin_dashboard_data

    context = get_admin_dashboard_data()

    return render(
        request,
        "admin/dashboard.html",
        context,
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