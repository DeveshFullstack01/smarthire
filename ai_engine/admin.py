from django.contrib import admin
from .models import InterviewQuestion


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "skill",
        "difficulty",
        "application",
        "created_at",
    )
