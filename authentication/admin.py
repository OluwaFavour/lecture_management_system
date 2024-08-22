from django.contrib import admin
from .models import User, Session


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "matric_number", "level", "is_lecturer"]
    search_fields = ["email", "matric_number"]
    list_filter = ["level", "is_class_rep", "is_lecturer"]
    ordering = ["email", "matric_number", "level"]
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "matric_number", "level", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_class_rep",
                    "is_lecturer",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "matric_number",
                    "level",
                    "password1",
                    "password2",
                    "is_class_rep",
                    "is_lecturer",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["token", "is_current", "is_first_login"]
    search_fields = ["token"]
    list_filter = ["is_current", "is_first_login"]
    ordering = ["token"]
    fieldsets = ((None, {"fields": ("token", "is_current", "is_first_login")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("token", "is_current", "is_first_login"),
            },
        ),
    )
