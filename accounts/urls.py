from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CandidateSignupView, RecruiterSignupView

urlpatterns = [
    path("signup/candidate/", CandidateSignupView.as_view(), name="candidate-signup"),
    path("signup/recruiter/", RecruiterSignupView.as_view(), name="recruiter-signup"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login-refresh"),
]
     




