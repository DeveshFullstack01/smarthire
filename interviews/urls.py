from django.urls import path

from . import views


urlpatterns = [

    path(
        "schedule/<int:application_id>/",
        views.schedule_interview,
        name="schedule-interview",
    ),

    path(
        "recruiter/",
        views.recruiter_interviews,
        name="recruiter-interviews",
    ),

    path(
        "candidate/",
        views.candidate_interviews,
        name="candidate-interviews",
    ),

    path(
        "<int:interview_id>/",
        views.interview_detail,
        name="interview-detail",
    ),

    path(
        "<int:interview_id>/respond/",
        views.respond_to_interview,
        name="interview-respond",
    ),

    path(
        "<int:interview_id>/feedback/",
        views.interview_feedback,
        name="interview-feedback",
    ),

    # ==================================================
    # Admin
    # ==================================================

    path(
        "admin/",
        views.admin_interviews,
        name="admin-interviews",
    ),
]