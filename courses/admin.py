from django.contrib import admin

from .models import Course


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "level",
        "lecturer",
        "day",
        "start_time",
        "end_time",
    ]
    list_filter = ["level", "day", "lecturer"]
    search_fields = ["code", "name", "lecturer__username"]
