from django.contrib import admin

from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "interview_type",
        "scheduled_at",
        "status",
    )

    list_filter = (
        "status",
        "interview_type",
    )

    search_fields = (
        "application__candidate__username",
        "application__job__title",
        "interviewer_name",
    )

    ordering = (
        "-scheduled_at",
    )
# Register your models here.
