from django.urls import path

from . import views


urlpatterns = [

    # ==========================================
    # Candidate
    # ==========================================
    path(
        "start/<int:offer_id>/",
        views.start_onboarding,
        name="start-onboarding",
    ),
    path(
        "my/",
        views.my_onboarding,
        name="my-onboarding",
    ),
    # ==========================================
    # Recruiter
    # ==========================================
    path(
        "recruiter/",
        views.recruiter_onboarding,
        name="recruiter-onboarding",
    ),
    path(
        "review/<int:onboarding_id>/",
        views.review_onboarding,
        name="review-onboarding",
    ),
    path(
         "admin/",
         views.admin_onboarding,
         name="admin-onboarding",
    ),
    path(
         "admin/<int:onboarding_id>/complete/",
         views.complete_onboarding,
         name="complete-onboarding",
    ),
    path(
    "admin/<int:onboarding_id>/",
    views.admin_onboarding_detail,
    name="admin-onboarding-detail",
    ),
]
