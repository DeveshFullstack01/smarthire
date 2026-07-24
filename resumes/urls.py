from django.urls import path

from .views import (
    upload_resume,
    view_resume,
    download_resume,
      resume_analysis,
)

urlpatterns = [

    path(
        "upload/<int:application_id>/",
        upload_resume,
        name="upload-resume",
    ),

    path(
        "view/<int:application_id>/",
        view_resume,
        name="view-resume",
    ),

    path(
        "download/<int:application_id>/",
        download_resume,
        name="download-resume",
    ),
    path(
    "analysis/<int:application_id>/",
    resume_analysis,
    name="resume-analysis",
    ),
]