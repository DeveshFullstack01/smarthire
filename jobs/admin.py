from django.contrib import admin

from .models import Company, Job


# ==========================================================
# COMPANY ADMIN
# ==========================================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    # ------------------------------------------------------
    # Company list
    # ------------------------------------------------------

    list_display = (
        "name",
        "owner",
    )

    list_display_links = (
        "name",
    )

    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
    )

    # ------------------------------------------------------
    # Ordering
    # ------------------------------------------------------

    ordering = (
        "name",
    )

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    list_per_page = 25


# ==========================================================
# JOB ADMIN
# ==========================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "location",
        "job_type",
        "salary",
        "created_at",
    )

    list_display_links = (
        "title",
    )

    list_filter = (
        "job_type",
        "location",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "company__name",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25