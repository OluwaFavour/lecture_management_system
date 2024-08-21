from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator,
    EmailValidator,
)
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(
        self,
        email: str | None = None,
        matric_number: str | None = None,
        level: int | None = None,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        is_lecturer = None
        is_student = None
        if not email and not matric_number:
            raise ValueError("The Email or Matric Number is required")
        if email and matric_number:
            raise ValueError("You can only use Email or Matric Number")
        if not password:
            raise ValueError("The Password is required")
        if email:
            if level:
                raise ValueError("The Level is not required")
            elif extra_fields.get("is_class_rep"):
                raise ValueError("The is_class_rep field is not required")
            email = self.normalize_email(email)
            is_lecturer = extra_fields.pop("is_lecturer", True)
        elif matric_number:
            if not level:
                raise ValueError("The Level is required")
            is_student = extra_fields.pop("is_student", True)
        user: "User" = self.model(
            email=email,
            matric_number=matric_number,
            level=level,
            is_lecturer=is_lecturer or False,
            is_student=is_student or False,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str | None = None,
        matric_number: str | None = None,
        password: str | None = None,
        **extra_fields,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(
            email, matric_number, level=None, password=password, **extra_fields
        )


class Level(models.IntegerChoices):
    LEVEL_100 = 100
    LEVEL_200 = 200
    LEVEL_300 = 300
    LEVEL_400 = 400
    LEVEL_500 = 500


class User(AbstractBaseUser):
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        validators=[EmailValidator(message="The Email is not valid")],
    )
    matric_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                r"^[A-Z]{3}/[0-9]{2}/[0-9]{4}$",
                message="The Matric Number is not valid, it should be in the format 'ABC/12/3456'",
            )
        ],
    )
    level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=Level.choices,
    )
    is_lecturer = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_class_rep = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "matric_number"
    REQUIRED_FIELDS = ["email", "level"]

    def __str__(self) -> str:
        return self.email if self.email else self.matric_number

    def has_perm(self, perm: str, obj: models.Model | None = None) -> bool:
        return True

    def has_module_perms(self, app_label: str) -> bool:
        return True

    def save(self, *args, **kwargs):
        if self.email:
            self.matric_number = None
        elif self.matric_number:
            self.email = None

        if self.is_student:
            self.is_lecturer = False
        if self.is_lecturer:
            self.is_student = False
        return super().save(*args, **kwargs)


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_first_login = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.email if self.user.email else self.user.matric_number

    def __repr__(self) -> str:
        return f"<Session: {self.user.email if self.user.email else self.user.matric_number}>"
