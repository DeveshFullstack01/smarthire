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

urlpatterns = [

    path("create/", create_job, name="create-job"),

    path("list/", job_list, name="job-list"),

    path("detail/<int:job_id>/", job_detail, name="job-detail"),

    path("update/<int:job_id>/", update_job, name="job-update"),

    path("delete/<int:job_id>/", delete_job, name="job-delete"),

    path("candidate/jobs/", candidate_job_list, name="candidate-job-list"),

    path("applicants/<int:job_id>/", job_applicants, name="job-applicants"),

]