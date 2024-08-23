from datetime import time, datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from courses.models import Course, SpecialCourse

# Create your models here.
User = get_user_model()


class Alert(models.Model):
    students = models.ManyToManyField(
        User, related_name="alerts", limit_choices_to={"is_lecturer": False}
    )
    event = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="alerts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    early_minutes = models.PositiveIntegerField(default=30)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)

    @property
    def should_alert(self):
        if not self.is_active:
            return False

        current_time = timezone.now()
        # Check if the alert should be triggered today
        if self.event.day != current_time.strftime("%a").upper():
            return False

        # Check if the alert should be triggered now
        alert_time = datetime.combine(
            current_time.date(), self.event.start_time
        ) - timedelta(minutes=self.early_minutes)
        return current_time >= alert_time

    def is_for_special_course(self):
        return isinstance(self.event, SpecialCourse)

    def get_course(self):
        return self.event

    def get_special_course(self) -> SpecialCourse | None:
        if self.is_for_special_course():
            return self.event
        return None

    def get_course_schedule(self) -> tuple[time, time]:
        start_time = self.event.start_time
        end_time = self.event.end_time
        return start_time, end_time

    def activate(self):
        self.is_active = True
        self.save(update_fields=["is_active"])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

    def __str__(self):
        return f"{self.title} - {self.event}"


class AlertSettings(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="alert_settings",
        limit_choices_to={"is_lecturer": False},
    )
    via_email = models.BooleanField(default=True)
    via_sms = models.BooleanField(default=False)

    def enable_email_alerts(self):
        self.via_email = True
        self.save(update_fields=["via_email"])

    def disable_email_alerts(self):
        self.via_email = False
        self.save(update_fields=["via_email"])

    def enable_sms_alerts(self):
        self.via_sms = True
        self.save(update_fields=["via_sms"])

    def disable_sms_alerts(self):
        self.via_sms = False
        self.save(update_fields=["via_sms"])

    def __str__(self):
        return f"Alert Settings for {self.user}"
