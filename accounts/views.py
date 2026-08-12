import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.views.generic import TemplateView

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CandidateSignupSerializer,
    CustomTokenObtainPairSerializer,
    RecruiterSignupSerializer,
)
from .tokens import email_verification_token


User = get_user_model()
logger = logging.getLogger(__name__)


class RegistrationSuccessView(TemplateView):
    template_name = "accounts/registration_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["email"] = self.request.session.get(
            "verification_email"
        )

        return context

def send_verification_email(user):
    """Send an email verification link to the user.

    Best-effort. On hosts that block outbound SMTP (e.g. Render's free
    tier) a blocking send would hang until the gunicorn worker is
    killed, so email is skipped entirely unless SEND_VERIFICATION_EMAIL
    is explicitly turned on, and even then it uses a short timeout and
    never raises.
    """

    logger.info(
        "Sending verification email to user_id=%s",
        user.id,
    )

    user.refresh_from_db()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = (
        f"{settings.FRONTEND_URL}/api/accounts/verify-email/{uid}/{token}/"
    )

    # DEBUG (Remove later)
    print("\n" + "=" * 80)
    print("USERNAME :", user.username)
    print("USER ID  :", user.pk)
    print("VERIFIED :", user.is_verified)
    print("UID      :", uid)
    print("TOKEN    :", token)
    print("VERIFY URL:")
    print(verify_url)
    print("=" * 80 + "\n")

    # Skip email entirely unless explicitly enabled. Default False so a
    # blocked/hanging SMTP connection can never take down signup.
    if not getattr(settings, "SEND_VERIFICATION_EMAIL", False):
        logger.info(
            "Verification email skipped (SEND_VERIFICATION_EMAIL is off). "
            "user_id=%s",
            user.id,
        )
        return False

    try:
        send_mail(
            subject="Verify your SmartHire account",
            message=(
                f"Hi {user.username},\n\n"
                f"Click the link below to verify your account:\n\n"
                f"{verify_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        logger.info(
            "Verification email sent to user_id=%s",
            user.id,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to send verification email to user_id=%s.",
            user.id,
        )

        return False


class CandidateSignupView(generics.CreateAPIView):
    """Register a new candidate."""

    serializer_class = CandidateSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.info("Creating candidate account.")

        user = serializer.save()

        logger.info(
            "Candidate account created. user_id=%s",
            user.id,
        )

        # DEMO MODE: auto-verify so the user can log in without email.
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        email_sent = send_verification_email(user)

        request.session["verification_email_sent"] = email_sent

        return redirect(reverse("registration-success"))


class RecruiterSignupView(generics.CreateAPIView):
    """Register a new recruiter."""

    serializer_class = RecruiterSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger.info("Creating recruiter account.")

        user = serializer.save()

        logger.info(
            "Recruiter account created. user_id=%s",
            user.id,
        )

        # DEMO MODE: auto-verify so the user can log in without email.
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        email_sent = send_verification_email(user)

        request.session["verification_email_sent"] = email_sent

        return redirect(reverse("registration-success"))


class VerifyEmailView(APIView):
    """Verify a user's email."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        logger.info("Email verification requested.")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            logger.warning("Invalid verification link.")

            return render(
                request,
                "accounts/email_verification_failed.html",
                {
                    "title": "Invalid Verification Link",
                    "message": (
                        "The verification link is invalid. "
                        "Please request a new verification email."
                    ),
                },
                status=400,
            )

        if email_verification_token.check_token(user, token):

            if not user.is_verified:
                user.is_verified = True
                user.save(update_fields=["is_verified"])

            logger.info(
                "Email verified successfully for user_id=%s",
                user.id,
            )

            return render(
                request,
                "accounts/email_verified.html",
            )

        logger.warning(
            "Expired or invalid verification token for user_id=%s",
            user.id,
        )

        return render(
            request,
            "accounts/email_verification_failed.html",
            {
                "title": "Verification Link Expired",
                "message": (
                    "This verification link has expired or is no longer valid."
                ),
            },
            status=400,
        )


class ResendVerificationView(APIView):
    """Resend verification email."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logger.info("Verification email resend requested.")

        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            logger.warning(
                "Verification resend requested for unknown email."
            )

            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_verified:
            logger.info(
                "Verification resend skipped. user_id=%s already verified.",
                user.id,
            )

            return Response(
                {"detail": "Your email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "Resending verification email to user_id=%s",
            user.id,
        )

        email_sent = send_verification_email(user)

        if not email_sent:
            return Response(
                {
                    "detail": (
                        "We couldn't send the email right now. "
                        "Please try again shortly."
                    )
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"message": "Verification email sent successfully."},
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Authenticate a user and issue JWT tokens."""

    serializer_class = CustomTokenObtainPairSerializer