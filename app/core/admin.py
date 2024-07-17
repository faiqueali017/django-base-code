"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    ordering = ["user_id"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_staff",
        "is_active",
    ]
    list_filter = ["is_staff", "is_active", "user_type"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal Info"),
            {
                "fields": ("first_name", "last_name", "image_id"),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_type",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "deleted_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_type",
                ),
            },
        ),
    )
    search_fields = ["email", "first_name", "last_name"]
    filter_horizontal = ()


@admin.register(models.OTP)
class OTPAdmin(admin.ModelAdmin):
    ordering = ["otp_id"]
    list_display = [
        "otp_id",
        "code",
        "user",
        "created_at",
        "used_at",
        "expires_at",
    ]


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    ordering = ["file_id"]
    list_display = ["file_id", "source_url", "file_type", "created_at"]
    list_filter = ["file_type"]
