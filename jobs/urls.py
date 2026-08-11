from django.urls import path

from .web_views import (
    candidate_job_list,
    create_job,
    delete_job,
    job_applicants,
    job_detail,
    job_list,
    update_job,
)

from . import admin_views


urlpatterns = [

    # ==================================================
    # Recruiter
    # ==================================================

    path(
        "create/",
        create_job,
        name="create-job",
    ),

    path(
        "list/",
        job_list,
        name="job-list",
    ),

    path(
        "detail/<int:job_id>/",
        job_detail,
        name="job-detail",
    ),

    path(
        "update/<int:job_id>/",
        update_job,
        name="job-update",
    ),

    path(
        "delete/<int:job_id>/",
        delete_job,
        name="job-delete",
    ),

    path(
        "applicants/<int:job_id>/",
        job_applicants,
        name="job-applicants",
    ),


    # ==================================================
    # Candidate
    # ==================================================

    path(
        "candidate/jobs/",
        candidate_job_list,
        name="candidate-job-list",
    ),


    # ==================================================
    # Admin
    # ==================================================

    path(
        "admin/",
        admin_views.admin_job_list,
        name="admin-job-list",
    ),

    path(
        "admin/<int:job_id>/",
        admin_views.admin_job_detail,
        name="admin-job-detail",
    ),

    path(
        "admin/<int:job_id>/edit/",
        admin_views.admin_edit_job,
        name="admin-edit-job",
    ),

    path(
        "admin/<int:job_id>/delete/",
        admin_views.admin_delete_job,
        name="admin-delete-job",
    ),

]