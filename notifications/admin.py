from django.contrib import admin

from .models import Notification


# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "created_at"]
    list_filter = ["creator", "created_at"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["read_by"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "creator",
                    "read_by",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "creator",
                )
            },
        ),
    )
