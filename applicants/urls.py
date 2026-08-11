from django.urls import path

from . import views
from . import admin_views


urlpatterns = [

    # ==================================================
    # Candidate
    # ==================================================

    path(
        "apply/<int:job_id>/",
        views.apply_job,
        name="apply-job",
    ),

    path(
        "my-applications/",
        views.my_applications,
        name="my-applications",
    ),


    # ==================================================
    # Recruiter
    # ==================================================

    path(
        "status/<int:application_id>/",
        views.update_application_status,
        name="update-application-status",
    ),

    path(
        "recruiter/job/<int:job_id>/applications/",
        views.recruiter_applications,
        name="recruiter-applications",
    ),

    path(
        "shortlist/<int:application_id>/",
        views.shortlist_candidate,
        name="shortlist-candidate",
    ),

    path(
        "reject/<int:application_id>/",
        views.reject_candidate,
        name="reject-candidate",
    ),


    # ==================================================
    # Admin
    # ==================================================

    path(
        "admin/",
        admin_views.admin_application_list,
        name="admin-applications",
    ),

]