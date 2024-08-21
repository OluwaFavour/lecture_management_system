from rest_framework.permissions import BasePermission

from .authentication_classes import SessionAuthentication


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        user, _ = SessionAuthentication().authenticate(request)
        return user.is_lecturer if user else False


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user, _ = SessionAuthentication().authenticate(request)
        return user.is_student if user else False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user, _ = SessionAuthentication().authenticate(request)
        return user.is_superuser or user.is_staff if user else False


class IsClassRep(BasePermission):
    def has_permission(self, request, view):
        user, _ = SessionAuthentication().authenticate(request)
        return user.is_class_rep if user else False
