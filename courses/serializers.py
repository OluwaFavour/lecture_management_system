from rest_framework import serializers

from .models import Course, DayOfWeek, Tag, SpecialCourse
from authentication.serializers import LecturerSerializer


class CourseLecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LecturerSerializer.Meta.model
        fields = ["id", "email", "is_lecturer", "is_registration_officer"]


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    lecturer = CourseLecturerSerializer(read_only=True)
    assistants = CourseLecturerSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        exclude = ["created_at", "updated_at"]


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ["created_at", "updated_at"]


class AssistantUpdateSerializer(serializers.Serializer):
    assistant = serializers.IntegerField()


class CourseForTheWeekSerializer(serializers.Serializer):
    day = serializers.ChoiceField(choices=DayOfWeek.choices, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)


class DayCourses:
    def __init__(self, day, courses):
        self.day = day
        self.courses = courses


class SpecialCourseSerializer(CourseSerializer):
    tag = serializers.ChoiceField(choices=Tag.choices)
