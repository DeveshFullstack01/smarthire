from django.contrib import admin

from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):

    # ==========================================================
    # INTERVIEW LIST
    # ==========================================================

    list_display = (
        "candidate_name",
        "job_title",
        "interview_type",
        "scheduled_at",
        "interviewer_name",
        "status",
    )

    list_display_links = (
        "candidate_name",
    )

    # ==========================================================
    # FILTERS
    # ==========================================================

    list_filter = (
        "status",
        "interview_type",
        "scheduled_at",
    )

    # ==========================================================
    # SEARCH
    # ==========================================================

    search_fields = (
        "application__candidate__username",
        "application__candidate__email",
        "application__job__title",
        "application__job__company__name",
        "interviewer_name",
    )

    # ==========================================================
    # ORDERING
    # ==========================================================

    ordering = (
        "-scheduled_at",
    )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    list_per_page = 25

    # ==========================================================
    # PERFORMANCE
    # ==========================================================

    list_select_related = (
        "application",
        "application__candidate",
        "application__job",
        "application__job__company",
    )

    # ==========================================================
    # DISPLAY HELPERS
    # ==========================================================

    @admin.display(
        description="Candidate",
        ordering="application__candidate__username",
    )
    def candidate_name(self, obj):
        return obj.application.candidate.username

    @admin.display(
        description="Job",
        ordering="application__job__title",
    )
    def job_title(self, obj):
        return obj.application.job.title