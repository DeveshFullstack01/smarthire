from django.urls import path

from .views import recruiter_dashboard

urlpatterns = [
    path(
        "recruiter/",
        recruiter_dashboard,
        name="recruiter-dashboard",
    ),
]