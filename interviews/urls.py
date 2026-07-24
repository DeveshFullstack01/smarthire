from django.urls import path

from . import views

urlpatterns = [
    path(
        "schedule/<int:application_id>/",
        views.schedule_interview,
        name="schedule-interview",
    ),
    path(
        "",
        views.recruiter_interviews,
        name="recruiter-interviews",
    ),
]