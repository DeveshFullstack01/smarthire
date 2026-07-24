from django.urls import path

from . import views

urlpatterns = [
    path(
        "generate/<int:application_id>/",
        views.generate_questions,
        name="generate-interview-questions",
    ),

    path(
        "interview/<int:application_id>/",
        views.interview_questions,
        name="interview-questions",
    ),
]