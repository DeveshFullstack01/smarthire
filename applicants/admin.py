from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    # ==========================================================
    # APPLICATION LIST
    # ==========================================================

    list_display = (
        "candidate",
        "job",
        "status",
        "applied_at",
    )

    list_display_links = (
        "candidate",
    )

    # ==========================================================
    # FILTERS
    # ==========================================================

    list_filter = (
        "status",
        "applied_at",
    )

    # ==========================================================
    # SEARCH
    # ==========================================================

    search_fields = (
        "candidate__username",
        "candidate__email",
        "job__title",
        "job__company__name",
    )

    # ==========================================================
    # ORDERING
    # ==========================================================

    ordering = (
        "-applied_at",
    )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    list_per_page = 25

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    list_select_related = (
        "candidate",
        "job",
        "job__company",
    )