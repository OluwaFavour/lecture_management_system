from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication.models import Level

User = get_user_model()


class DayOfWeek(models.TextChoices):
    MONDAY = "MON", _("Monday")
    TUESDAY = "TUE", _("Tuesday")
    WEDNESDAY = "WED", _("Wednesday")
    THURSDAY = "THU", _("Thursday")
    FRIDAY = "FRI", _("Friday")
    SATURDAY = "SAT", _("Saturday")
    SUNDAY = "SUN", _("Sunday")


# Create your models here.
class Course(models.Model):
    # Course details
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                r"[A-Z]{3}[0-9]{3}", message="The code must be in the format ABC123"
            )
        ],
    )
    level = models.PositiveIntegerField(
        choices=Level.choices,
    )
    lecturer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lecturer_courses",
        limit_choices_to={"is_lecturer": True},
    )
    assistants = models.ManyToManyField(
        User,
        related_name="assisted_courses",
        limit_choices_to={"is_lecturer": True},
        blank=True,
    )

    # Schedule details
    day = models.CharField(max_length=3, choices=DayOfWeek)
    venue = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if self.start_time >= self.end_time:
            raise ValueError("The start time must be before the end time")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name", "code", "level", "day", "start_time"]


class Tag(models.TextChoices):
    CARRY_OVER = "CO", _("Carry Over")
    SPILL_OVER = "SO", _("Spill Over")


class SpecialCourse(Course):
    tag = models.CharField(max_length=100, choices=Tag.choices)
    students = models.ManyToManyField(
        User,
        related_name="special_courses",
        limit_choices_to={"is_lecturer": False},
    )
    base_course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name="special_course",
        parent_link=True,
        primary_key=True,
    )

    class Meta:
        ordering = ["name", "code", "level", "day", "start_time"]
        verbose_name = "Special Course"
        verbose_name_plural = "Special Courses"

    def __str__(self):
        return f"{self.code} - {self.name}"
