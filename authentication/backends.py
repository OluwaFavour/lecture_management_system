from typing import Any
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest

from .models import User


class UserModelBackend(BaseBackend):

    def authenticate(
        self,
        request: HttpRequest,
        username: str | None = ...,
        password: str | None = ...,
        **kwargs: Any
    ) -> AbstractUser | None:
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None:
            username = kwargs.get(UserModel.EMAIL_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(matric_number=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                UserModel().set_password(password)
                return
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a nonexistent user (#20760).
        UserModel().set_password(password)
        return

    def get_user(self, user_id: int) -> AbstractUser | None:
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return

    def user_can_authenticate(self, user: AbstractUser) -> bool:
        return user.is_active
