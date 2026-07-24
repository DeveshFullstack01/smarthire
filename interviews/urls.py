from django.urls import path

from . import views

urlpatterns = [

    # Recruiter
    path(
        "",
        views.recruiter_interviews,
        name="recruiter-interviews",
    ),
    path(
        "schedule/<int:application_id>/",
        views.schedule_interview,
        name="schedule-interview",
    ),

    # Candidate
    path(
        "my/",
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
]