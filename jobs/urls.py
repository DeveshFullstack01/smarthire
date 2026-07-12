from django.urls import path
from .views import JobCreateView

urlpatterns = [
    path("create/", JobCreateView.as_view(), name="job-create"),
]