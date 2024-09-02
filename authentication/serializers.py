from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator, RegexValidator

from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

from .models import Session

# from courses.serializers import get_course_serializer_class

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        write_only=True,
    )
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    is_first_login = serializers.BooleanField(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def validate_username(self, value: str) -> str:
        email_validator = EmailValidator()
        matric_number_validator = RegexValidator(r"^[A-Z]{3}/[0-9]{2}/[0-9]{4}$")

        try:
            email_validator(value)
            return value
        except DjangoValidationError:
            try:
                matric_number_validator(value)
                return value
            except DjangoValidationError as e:
                raise serializers.ValidationError(
                    "The username must be an email or a matric number."
                )


class LecturerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    lecturer_courses = serializers.SerializerMethodField()
    assisted_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "password",
            "email",
            "is_lecturer",
            "lecturer_courses",
            "assisted_courses",
        ]
        read_only_fields = ["is_lecturer"]

    def get_lecturer_courses(self, obj):
        from courses.serializers import (
            CourseSerializer,
        )  # Import here to avoid circular import

        courses = obj.lecturer_courses.all()
        return CourseSerializer(courses, many=True).data

    def get_assisted_courses(self, obj):
        from courses.serializers import (
            CourseSerializer,
        )  # Import here to avoid circular import

        courses = obj.assisted_courses.all()
        return CourseSerializer(courses, many=True).data

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("The email address is already in use.")
        return value

    def create(self, validated_data: dict[str, Any]):
        return User.objects.create_user(
            password=validated_data.pop("password"),
            is_lecturer=True,
            **validated_data,
        )


class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "password",
            "matric_number",
            "level",
            "is_lecturer",
            "is_class_rep",
        ]
        read_only_fields = ["is_lecturer", "is_class_rep"]

    def validate_matric_number(self, value: str) -> str:
        if User.objects.filter(matric_number=value).exists():
            raise serializers.ValidationError("The matric number is already in use.")
        return value

    def create(self, validated_data: dict[str, Any]):
        return User.objects.create_user(
            password=validated_data.pop("password"),
            **validated_data,
        )
