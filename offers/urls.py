from django.urls import path

from . import views

urlpatterns = [

    # ==========================================
    # Recruiter
    # ==========================================

    path(
        "create/<int:application_id>/",
        views.create_offer,
        name="create-offer",
    ),

    path(
        "recruiter/",
        views.recruiter_offers,
        name="recruiter-offers",
    ),

    # ==========================================
    # Candidate
    # ==========================================

    path(
        "my/",
        views.my_offers,
        name="my-offers",
    ),

    path(
        "<int:offer_id>/<str:action>/",
        views.respond_offer,
        name="respond-offer",
    ),

]