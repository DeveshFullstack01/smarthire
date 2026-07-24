from django.urls import path

from .views import (
    apply_job,
    update_application_status,
    my_applications,
    recruiter_applications,
    shortlist_candidate,
    reject_candidate,
)

urlpatterns = [
    path(
        "apply/<int:job_id>/",
        apply_job,
        name="apply-job",
    ),
    path(
        "status/<int:application_id>/",
        update_application_status,
        name="update-application-status",
    ),
    path(
        "my-applications/",
        my_applications,
        name="my-applications",
    ),
    path(
        "recruiter/job/<int:job_id>/applications/",
        recruiter_applications,
        name="recruiter-applications",
    ),
    path(
        "shortlist/<int:application_id>/",
        shortlist_candidate,
        name="shortlist-candidate",
    ),
    path(
        "reject/<int:application_id>/",
        reject_candidate,
        name="reject-candidate",
    ),
]