from pathlib import Path
from datetime import timedelta
import os

from decouple import config


# ============================================================
# Base Directory
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# Security
# ============================================================

# Required in deployment.
# Do not provide a production fallback secret.
SECRET_KEY = config("SECRET_KEY")

DEBUG = config(
    "DEBUG",
    default=True,
    cast=bool,
)

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]


# ============================================================
# Security Settings
# ============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"


# ------------------------------------------------------------
# CSRF Trusted Origins
# ------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config(
        "CSRF_TRUSTED_ORIGINS",
        default="http://localhost,http://127.0.0.1",
    ).split(",")
    if origin.strip()
]


# ------------------------------------------------------------
# HTTPS Security
# ------------------------------------------------------------

SECURE_SSL_REDIRECT = config(
    "SECURE_SSL_REDIRECT",
    default=False,
    cast=bool,
)

if SECURE_SSL_REDIRECT:

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    # Django is behind a reverse proxy such as Nginx
    # which terminates HTTPS.
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


# ============================================================
# Installed Apps
# ============================================================

INSTALLED_APPS = [

    # ASGI / WebSocket
    "daphne",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # REST API
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    # Channels
    "channels",

    # SmartHire applications
    "accounts",
    "jobs",
    "applicants",
    "resumes",
    "notifications",
    "ai_engine",
    "dashboard",
    "interviews",
    "offers",
    "onboarding",
]


AUTH_USER_MODEL = "accounts.User"


# ============================================================
# Middleware
# ============================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ============================================================
# Templates
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

                "notifications.context_processors.notifications",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# ============================================================
# Database
# ============================================================

DB_HOST = config(
    "DB_HOST",
    default="localhost",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",

        "NAME": config("DB_NAME"),

        "USER": config("DB_USER"),

        "PASSWORD": config("DB_PASSWORD"),

        "HOST": DB_HOST,

        "PORT": config("DB_PORT"),
    }
}


# ============================================================
# Password Validators
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# Internationalization
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# Static Files
# ============================================================

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# Media Files
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# Django REST Framework
# ============================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",

        "rest_framework.authentication.SessionAuthentication",
    ),
}


# ============================================================
# JWT
# ============================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
}


# ============================================================
# Email Configuration
# ============================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = config(
    "EMAIL_HOST",
    default="smtp.gmail.com",
)

EMAIL_PORT = config(
    "EMAIL_PORT",
    default=587,
    cast=int,
)

EMAIL_USE_TLS = config(
    "EMAIL_USE_TLS",
    default=True,
    cast=bool,
)

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "noreply@smarthire.com"

# Fail fast instead of hanging if the SMTP host is unreachable
# (e.g. outbound SMTP blocked on Render free tier).
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=10, cast=int)

# Master switch for verification email. Off by default so signup can
# never hang/crash on hosts that block SMTP. Turn on only once a real
# email provider (SendGrid/Resend/etc.) is configured.
SEND_VERIFICATION_EMAIL = config(
    "SEND_VERIFICATION_EMAIL",
    default=False,
    cast=bool,
)


# ============================================================
# Application Base URL
# ============================================================

# Used for verification links and notification links.
FRONTEND_URL = config(
    "FRONTEND_URL",
    default="https://smarthire-cndr.onrender.com",
)


# ============================================================
# Default Primary Key
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# Logging
# ============================================================

LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "standard": {

            "format": (
                "%(asctime)s | "
                "%(levelname)-8s | "
                "%(name)s | "
                "%(message)s"
            ),
        },
    },

    "handlers": {

        "console": {

            "class": "logging.StreamHandler",

            "formatter": "standard",
        },
    },

    "root": {

        "handlers": ["console"],

        "level": "INFO",
    },
}


# ============================================================
# Django Channels / Redis
# ============================================================

REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "127.0.0.1",
)

CHANNEL_LAYERS = {

    "default": {

        "BACKEND": (
            "channels_redis.core.RedisChannelLayer"
        ),

        "CONFIG": {

            "hosts": [
                (REDIS_HOST, 6379),
            ],
        },
    },
}


# ============================================================
# Authentication / Redirects
# ============================================================

LOGIN_URL = "/api/accounts/web/login/"

LOGIN_REDIRECT_URL = "/api/accounts/web/redirect/"

LOGOUT_REDIRECT_URL = "/api/accounts/web/login/"