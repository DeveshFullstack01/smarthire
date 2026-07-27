from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from dashboard.views import recruiter_dashboard
from .views import (
    CandidateSignupView,
    RecruiterSignupView,
    VerifyEmailView,
    CustomTokenObtainPairView,
    ResendVerificationView,
)
from .web_views import (
    login_page,
    logout_page,
    admin_dashboard,
    candidate_dashboard,
)

from .profile_views import (
    my_profile,
    edit_profile,
    add_skill,
    delete_skill,
)
urlpatterns = [
    # ==========================
    # Web Pages
    # ==========================
    path(
        "web/login/",
        login_page,
        name="web-login",
    ),
    path(
        "web/logout/",
        logout_page,
        name="web-logout",
    ),
    path(
        "web/admin/dashboard/",
        admin_dashboard,
        name="admin-dashboard",
    ),
    path(
        "web/recruiter/dashboard/",
        recruiter_dashboard,
        name="recruiter-dashboard",
    ),
    path(
        "web/candidate/dashboard/",
        candidate_dashboard,
        name="candidate-dashboard",
    ),

    # ==========================
    # Authentication APIs
    # ==========================
    path(
        "signup/candidate/",
        CandidateSignupView.as_view(),
        name="candidate-signup",
    ),
    path(
        "signup/recruiter/",
        RecruiterSignupView.as_view(),
        name="recruiter-signup",
    ),
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="login",
    ),
    path(
        "login/refresh/",
        TokenRefreshView.as_view(),
        name="login-refresh",
    ),

    # ==========================
    # Email Verification
    # ==========================
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    
    path(
        "web/candidate/profile/edit/",
        edit_profile,
        name="edit-profile",
    ),
    path(
        "web/candidate/profile/skill/add/",
        add_skill,
        name="add-skill",
    ),
    path(
        "web/candidate/profile/skill/<int:skill_id>/delete/",
        delete_skill,
        name="delete-skill",
    ),
    
    
    
    
    
    
]