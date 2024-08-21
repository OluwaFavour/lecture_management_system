from django.contrib import admin
from django.utils import timezone

from .models import Message


# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "text", "timestamp", "is_read")
    list_filter = ("is_read",)
    search_fields = ("sender__username", "recipient__username", "text")
    readonly_fields = ("timestamp", "read_at")
    actions = ["mark_as_read"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, "Messages marked as read.")

    mark_as_read.short_description = "Mark selected messages as read"
