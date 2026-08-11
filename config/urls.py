from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.views import health_check
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from django.shortcuts import render

def home(request):
    if request.user.is_authenticated:
        if request.user.role == "recruiter":
            return redirect("recruiter-dashboard")
        return redirect("candidate-job-list")

    return render(request, "index.html")

urlpatterns = [
    path("health/", health_check, name="health"),
    path("", home, name="home"),
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
    path("offers/", include("offers.urls")),
    path("onboarding/", include("onboarding.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )