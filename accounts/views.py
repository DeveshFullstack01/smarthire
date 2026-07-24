import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

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

logger = logging.getLogger(__name__)

User = get_user_model()


def send_verification_email(user):
    """Send an email verification link to the user."""

    logger.info(
        "Sending verification email to user_id=%s",
        user.id,
    )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = (
        f"{settings.FRONTEND_URL}/api/accounts/verify-email/{uid}/{token}/"
    )

    send_mail(
        subject="Verify your SmartHire account",
        message=(
            f"Hi {user.username},\n\n"
            f"Click the link below to verify your account:\n"
            f"{verify_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    logger.info(
        "Verification email sent to user_id=%s",
        user.id,
    )


class CandidateSignupView(generics.CreateAPIView):
    """Register a new candidate account."""

    serializer_class = CandidateSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        logger.info("Creating candidate account.")

        user = serializer.save()

        logger.info(
            "Candidate account created. user_id=%s",
            user.id,
        )

        send_verification_email(user)


class RecruiterSignupView(generics.CreateAPIView):
    """Register a new recruiter account."""

    serializer_class = RecruiterSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        logger.info("Creating recruiter account.")

        user = serializer.save()

        logger.info(
            "Recruiter account created. user_id=%s",
            user.id,
        )

        send_verification_email(user)


class VerifyEmailView(APIView):
    """Verify a user's email address."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        logger.info("Email verification requested.")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            logger.warning("Invalid email verification link.")

            return Response(
                {"error": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email_verification_token.check_token(user, token):
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            logger.info(
                "Email verified successfully for user_id=%s",
                user.id,
            )

            return Response(
                {"message": "Email verified successfully."},
                status=status.HTTP_200_OK,
            )

        logger.warning(
            "Expired or invalid verification token for user_id=%s",
            user.id,
        )

        return Response(
            {"error": "Verification link is invalid or has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendVerificationView(APIView):
    """Resend the email verification link."""

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

        send_verification_email(user)

        return Response(
            {"message": "Verification email sent successfully."},
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Authenticate a user and issue JWT access/refresh tokens."""

    serializer_class = CustomTokenObtainPairSerializer