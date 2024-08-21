from typing import Any

from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator, RegexValidator

from .models import Session

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


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "matric_number",
            "level",
            "is_lecturer",
            "is_student",
        ]
        read_only_fields = ["email", "matric_number", "is_lecturer", "is_student"]
        extra_kwargs = {
            "email": {"required": False},
            "matric_number": {"required": False},
            "level": {"required": False},
        }

    def validate_username(self, value: str) -> str:
        email_validator = EmailValidator()
        matric_number_validator = RegexValidator(r"^[A-Z]{3}/[0-9]{2}/[0-9]{4}$")

        try:
            email_validator(value)
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "The email address is already in use."
                )
            return value
        except DjangoValidationError:
            try:
                matric_number_validator(value)
                if User.objects.filter(matric_number=value).exists():
                    raise serializers.ValidationError(
                        "The matric number is already in use."
                    )
                return value
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)

    # def validate_password(self, value: str) -> str:
    #     try:
    #         password_validation.validate_password(value)
    #         return value
    #     except DjangoValidationError as e:
    #         raise serializers.ValidationError(e.messages)

    def create(self, validated_data: dict[str, Any]):
        email_validator = EmailValidator()

        username = validated_data.pop("username")
        password = validated_data.pop("password")
        email = None
        matric_number = None

        try:
            email_validator(username)
            email = username
        except DjangoValidationError:
            matric_number = username

        if email and validated_data.get("level"):
            raise serializers.ValidationError(
                "The Level is not required for lecturers."
            )
        elif matric_number and not validated_data.get("level"):
            raise serializers.ValidationError("The Level is required for students.")
        if email:
            is_lecturer = validated_data.pop("is_lecturer", True)
            return User.objects.create_user(
                email=email,
                password=password,
                is_lecturer=is_lecturer,
                **validated_data,
            )
        elif matric_number:
            is_student = validated_data.pop("is_student", True)
            return User.objects.create_user(
                matric_number=matric_number,
                level=validated_data.pop("level"),
                password=password,
                is_student=is_student,
                **validated_data,
            )
        else:
            raise serializers.ValidationError(
                "The username must be an email or a matric number."
            )
