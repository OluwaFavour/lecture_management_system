from django.contrib import admin

from .models import Alert, AlertSettings

# Register your models here.


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "timestamp", "is_active")
    list_filter = ("is_active", "event")
    search_fields = ("title", "description")
    date_hierarchy = "timestamp"
    actions = ["activate", "deactivate"]


@admin.register(AlertSettings)
class AlertSettingsAdmin(admin.ModelAdmin):
    list_display = ("student", "via_email", "via_sms")
    list_filter = ("via_email", "via_sms")
    search_fields = ("student__email",)
    actions = [
        "enable_email_alerts",
        "disable_email_alerts",
        "enable_sms_alerts",
        "disable_sms_alerts",
    ]
