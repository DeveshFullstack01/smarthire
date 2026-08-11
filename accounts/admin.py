from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # ==========================================================
    # USER LIST PAGE
    # ==========================================================

    list_display = (
        "username",
        "email",
        "role",
        "verification_status",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_display_links = (
        "username",
    )

    # Filters shown on the right side
    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )

    # Search box
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    # Default ordering
    ordering = (
        "-date_joined",
    )

    # Number of users per page
    list_per_page = 25

    # ==========================================================
    # CUSTOM DISPLAY
    # ==========================================================

    @admin.display(
        description="Verification",
        boolean=True,
    )
    def verification_status(self, obj):
        return obj.is_verified

    # ==========================================================
    # USER EDIT PAGE
    # ==========================================================

    fieldsets = (
        (
            "Login Information",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "SmartHire ATS Role",
            {
                "fields": (
                    "role",
                    "is_verified",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    # Fields that should not be manually edited
    readonly_fields = (
        "last_login",
        "date_joined",
    )

    # ==========================================================
    # ADD USER PAGE
    # ==========================================================

    add_fieldsets = (
        (
            "Create User",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_verified",
                ),
            },
        ),
    )