import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from jobs.models import Job

from .models import User
from .serializers import (
    CandidateSignupSerializer,
    RecruiterSignupSerializer,
)

logger = logging.getLogger(__name__)


# ==================================================
# Helper
# ==================================================
def _render_signup_errors(request, template, serializer):
    """Display serializer validation errors in HTML form."""

    for field, errors in serializer.errors.items():
        label = field.replace("_", " ").title()
        messages.error(request, f"{label}: {errors[0]}")

    return render(request, template)


# ==================================================
# Candidate Signup
# ==================================================
def candidate_signup_page(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        serializer = CandidateSignupSerializer(
            data={
                "username": request.POST.get("username"),
                "email": request.POST.get("email"),
                "password": request.POST.get("password"),
            }
        )

        if serializer.is_valid():

            from .views import send_verification_email

            user = serializer.save()

            # DEMO MODE: Render's free tier blocks outbound SMTP, so
            # verification email can't be delivered. Auto-verify the
            # account so the user can log in immediately. Remove this
            # block (and re-enable email) once a real email provider
            # is configured.
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            request.session["verification_email"] = user.email

            # Best-effort only: never let email break signup.
            send_verification_email(user)

            logger.info(
                "Candidate signed up via web. user_id=%s",
                user.id,
            )

            return redirect("registration-success")

        return _render_signup_errors(
            request,
            "accounts/candidate_signup.html",
            serializer,
        )

    return render(
        request,
        "accounts/candidate_signup.html",
    )


# ==================================================
# Recruiter Signup
# ==================================================
def recruiter_signup_page(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        serializer = RecruiterSignupSerializer(
            data={
                "username": request.POST.get("username"),
                "email": request.POST.get("email"),
                "password": request.POST.get("password"),
                "company_name": request.POST.get("company_name"),
            }
        )

        if serializer.is_valid():

            from .views import send_verification_email

            user = serializer.save()

            # DEMO MODE: auto-verify (see candidate_signup_page note).
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            request.session["verification_email"] = user.email

            # Best-effort only: never let email break signup.
            send_verification_email(user)

            logger.info(
                "Recruiter signed up via web. user_id=%s",
                user.id,
            )

            return redirect("registration-success")

        return _render_signup_errors(
            request,
            "accounts/recruiter_signup.html",
            serializer,
        )

    return render(
        request,
        "accounts/recruiter_signup.html",
    )


# ==================================================
# Login
# ==================================================
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


# ==================================================
# Logout
# ==================================================
def logout_page(request):

    logout(request)

    return redirect("web-login")


# ==================================================
# Redirect
# ==================================================
def redirect_user(user):

    if user.role == User.Role.ADMIN:
        return redirect("admin-dashboard")

    if user.role == User.Role.RECRUITER:
        return redirect("recruiter-dashboard")

    return redirect("candidate-dashboard")


# ==================================================
# Admin Dashboard
# ==================================================
@login_required
@role_required(User.Role.ADMIN)
def admin_dashboard(request):

    from .admin_dashboard_service import (
        get_admin_dashboard_data,
    )

    context = get_admin_dashboard_data()

    return render(
        request,
        "admin/dashboard.html",
        context,
    )


# ==================================================
# Candidate Dashboard
# ==================================================
@login_required
@role_required(User.Role.CANDIDATE)
def candidate_dashboard(request):

    from .candidate_dashboard_service import (
        get_candidate_dashboard_data,
    )

    context = get_candidate_dashboard_data(
        request.user,
    )

    return render(
        request,
        "candidate/dashboard.html",
        context,
    )