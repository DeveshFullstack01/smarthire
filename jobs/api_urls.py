from django.urls import path

from .api_views import JobCreateView

urlpatterns = [
    path(
        "create/",
        JobCreateView.as_view(),
        name="api-job-create",
    ),
]