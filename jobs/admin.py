from django.contrib import admin

from .models import Company, Job


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
    )

    search_fields = (
        "name",
        "owner__username",
    )


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