from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.views import health_check
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def home_redirect(request):
    if request.user.role == "recruiter":
        return redirect("recruiter-dashboard")
    return redirect("candidate-job-list")

urlpatterns = [
    path("health/", health_check, name="health"),
    path("", home_redirect, name="home"),
    path("admin/", admin.site.urls),

    path("api/accounts/", include("accounts.urls")),
    path("api/jobs/", include("jobs.api_urls")),

    path("dashboard/", include("dashboard.urls")),

    path("jobs/", include("jobs.urls")),
    path("applicants/", include("applicants.urls")),
    path("resumes/", include("resumes.urls")),
    path("ai/", include("ai_engine.urls")),
    path("interviews/", include("interviews.urls")),
    path("notifications/", include("notifications.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )