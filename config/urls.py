from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.views import health_check

urlpatterns = [
    # Health Check
    path("health/", health_check, name="health"),

    # Admin
    path("admin/", admin.site.urls),

    # API Routes
    path("api/accounts/", include("accounts.urls")),
    path("api/jobs/", include("jobs.api_urls")),

    # Dashboard
    path("dashboard/", include("dashboard.urls")),

    # Web Routes
    path("jobs/", include("jobs.urls")),
    path("applicants/", include("applicants.urls")),
    path("resumes/", include("resumes.urls")),
    path("ai/", include("ai_engine.urls")),
    path("interviews/", include("interviews.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )