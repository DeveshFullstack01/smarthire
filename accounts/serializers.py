import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from jobs.models import Company

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Authenticate user and return JWT tokens."""

    def validate(self, attrs):
        logger.info("Login attempt initiated.")

        data = super().validate(attrs)

        if not self.user.is_verified:
            logger.warning(
                "Login blocked for unverified user_id=%s",
                self.user.id,
            )

            raise AuthenticationFailed(
                "Please verify your email before logging in."
            )

        logger.info(
            "User logged in successfully. user_id=%s",
            self.user.id,
        )

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
        }

        return data


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CandidateSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            logger.warning(
                "Candidate signup failed. Username already exists."
            )

            raise serializers.ValidationError(
                "A user with that username already exists."
            )

        return value

    def create(self, validated_data):
        logger.info("Creating candidate user.")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=User.Role.CANDIDATE,
        )

        logger.info(
            "Candidate user created successfully. user_id=%s",
            user.id,
        )

        return user


class RecruiterSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    company_name = serializers.CharField(
        write_only=True,
        max_length=255,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "company_name",
        )

    def create(self, validated_data):
        logger.info("Creating recruiter user.")

        company_name = validated_data.pop("company_name")

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                role=User.Role.RECRUITER,
            )

            Company.objects.create(
                name=company_name,
                owner=user,
            )

        logger.info(
            "Recruiter user created successfully. user_id=%s",
            user.id,
        )

        return user