from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "uploaded_at",
        "updated_at",
    )

    search_fields = (
        "application__candidate__username",
        "application__candidate__email",
        "application__job__title",
    )

    list_select_related = (
        "application",
        "application__candidate",
        "application__job",
    )

    ordering = (
        "-uploaded_at",
    )